from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from people.models import Place
from people.models import Contact
import string

import const

# define WIDGETS
class PlaceWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.HiddenInput({ 'value': 0 }),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            #forms.TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=const.STATE_CHOICES),
        )
        super(PlaceWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            p = Place.objects.get(pk=value)
            return [p.id, p.name, p.zipcode, p.city, p.province]
        else:
            return ['','','','','']

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="placewidget">%s %s %s<br />%s %s %s %s %s %s</p>' % (
            _('Name:'), rendered_widgets[1],rendered_widgets[0],
            _('ZIP:'), rendered_widgets[2],
            _('City:'), rendered_widgets[3],
            _('State:'), rendered_widgets[4],
        ))



class ContactWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        attrs.update({ 'style' : 'margin-right: 0.5em' })
        widget = (
            forms.HiddenInput(attrs={ 'value':0 }),
            forms.Select(attrs=attrs,choices=const.FLAVOUR_CHOICES),
            forms.TextInput(attrs=attrs),
        )
        super(ContactWidget, self).__init__(widget, attrs)

    def decompress(self, value):
        if value:
            c = Contact.objects.get(pk=value)
            return [c.id, c.flavour, c.value]
        else:
            return ['','','']    

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="contactwidget">%s %s %s %s %s</p>' % (
            _('Type:'), rendered_widgets[1],
            _('Contact:'), rendered_widgets[2],
            rendered_widgets[0],
        ))


# define FORMS
class PlaceField(forms.MultiValueField):
#    fields = ['address','city']
    widget = PlaceWidget

    def __init__(self, *args, **kw):
        fields = (
            forms.IntegerField(), # was: label=_("id")
            forms.CharField(label=_("name")),
            forms.CharField(label=_("zip")),
            forms.CharField(label=_("city")),
            forms.ChoiceField(label=_("state"),choices=const.STATE_CHOICES),
        )
        super(PlaceField, self).__init__(fields, *args, **kw)

# a validator is not really needed here    
#    def validate(self, values):
#        return True

    def compress(self, data_list):
        if data_list != 0:
            curr_id = data_list[0]
            name = data_list[1]
            zipcode = data_list[2]
            city = data_list[3]
            state = data_list[4]

            if curr_id:
                # get the first object with the same id (should be exactly 1)
                curr_place = Place.objects.filter(id=curr_id)[0]
                curr_place.name = name
                curr_place.zipcode = zipcode
                curr_place.city = city
                curr_place.province = state
            else:
                curr_place = Place(name=name,zipcode=zipcode,
                    city=city,province=state)

            curr_place.save()

            return curr_place
        else: 
            return ''

class ContactField(forms.MultiValueField):
    widget = ContactWidget

    def __init__(self, *args, **kw):
        fields = (
            forms.IntegerField(),
            forms.ChoiceField(choices=const.FLAVOUR_CHOICES,label=_('flavour')),
            forms.CharField(label=_('contact')),
        )
        super(ContactField, self).__init__(fields, *args, **kw)
    
    def compress(self, data_list):
        if data_list:
            curr_id = data_list[0]
            flavour = data_list[1]
            contact = data_list[2]

            if curr_id:
                curr_cont = Contact.objects.filter(pk=curr_id)[0]
                curr_cont.flavour = flavour
                curr_cont.value = contact
            else:
                curr_cont = Contact(flavour=flavour,value=contact)

            # update/save the object if contact is specified; delete otherwise
            if (curr_cont.value == ''):
                if (curr_id):
                    # delete
                    curr_cont.delete()
                # else -> object not present in db, skip
            else:
                curr_cont.save()
            return curr_cont
        else: 
            return ''

class MultiContactWidget(forms.MultiWidget):
    num_contacts = 0

    def getSize(self):
        return MultiContactWidget.num_contacts

    def __init__(self, n, attrs=None):
        widgets = []
        MultiContactWidget.num_contacts = n
        for i in range(n):
            widgets.append(ContactWidget())

        super(MultiContactWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            contactIdSet = value.split("::")[0:MultiContactWidget.num_contacts]

            contacts = []
            for currId in contactIdSet:
                if currId.isdigit():
                    print("Search pk=",currId)
                    contactFound = Contact.objects.filter(pk=currId)
                    print("Found=",contactFound)
                    if contactFound != None:
                        contacts.append(contactFound)
            
            print("All contacts=",contacts)
            return contacts
        else:
            return ''

class MultiContactField(forms.MultiValueField):
    widget = MultiContactWidget(1)

    def __init__(self, n, *args, **kw):
        fields = []

        for i in range(n):
            fields.append(ContactField())

        MultiContactField.widget = MultiContactWidget(n)

        super(MultiContactField, self).__init__(fields, *args, **kw)

    def clean(self, value):
        print("Clean data=",value)
        emailFound = False
        for currData in value:
            if currData[1] == 'email' and currData[2].strip() != '':
                # at least one email contact -> OK
                emailFound = True
                break
                
        if not emailFound:
            # no email -> ValidationError
            raise forms.ValidationError("At least an email contact expected")

        return super(MultiContactField,self).clean(value)

    def compress(self, data_list):
# TODO could we cut the data_list in case it's longer than widget size?
        if len(data_list) != MultiContactField.widget.getSize():
            raise Exception("%d items expected, %d received" %
                MultiContactField.widget.getSize(),
                len(data_list))

        contactIdList = [] # array('I')
        emailFound = False
        for currContact in data_list:
            contactIdList.append(str(currContact.pk))
            emailFound = emailFound or (currContact.flavour == "email")

        if emailFound == False:
            raise forms.ValidationError("Email contact expected but not found")

        result = string.join(contactIdList,"::")
        return result
