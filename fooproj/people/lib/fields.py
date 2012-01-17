from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.validators import validate_email
from fooproj.people.lib.validators import validate_phone

from fooproj.people.models import Place
from fooproj.people.models import Contact
import string

from fooproj.people.const import STATE_CHOICES
from fooproj.people.const import CONTACT_CHOICES
from django.core.exceptions import ValidationError

# define WIDGETS
class PlaceWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.HiddenInput({ 'value': 0 }),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            #forms.TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=STATE_CHOICES),
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
            _('Name/Address:'), rendered_widgets[1],rendered_widgets[0],
            _('ZIP:'), rendered_widgets[2],
            _('City:'), rendered_widgets[3],
            _('State:'), rendered_widgets[4],
        ))



class ContactWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        attrs.update({ 'style' : 'margin-right: 0.5em' })
        widget = (
            forms.HiddenInput(attrs={ 'value':0 }),
            forms.Select(attrs=attrs,choices=CONTACT_CHOICES),
            forms.TextInput(attrs=attrs),
            forms.CheckboxInput(attrs=attrs)
        )
        super(ContactWidget, self).__init__(widget, attrs)

    def decompress(self, value):
        if value:
            c = Contact.objects.get(pk=value)
            return [c.id, c.flavour, c.value,c.is_preferred]
        else:
            return ['','','','']    

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="contactwidget">%s %s %s %s %s %s %s</p>' % (
            _('Type')+":", rendered_widgets[1],
            _('Contact')+":", rendered_widgets[2],
            rendered_widgets[0],
            _('Preferred')+":", rendered_widgets[3]
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
            forms.ChoiceField(label=_("state"),choices=STATE_CHOICES),
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
                curr_place = Place.objects.get(pk=curr_id)
                curr_place.name = name
                curr_place.zipcode = zipcode
                curr_place.city = city
                curr_place.province = state
            else:
                curr_place = Place(
                    name=name,zipcode=zipcode,
                    city=city,province=state
                )

            curr_place.save()

            return curr_place
        else: 
            return ''

    def clean(self, data_list):
        print("Clean PlaceField, DL=",data_list)
        nameaddr = data_list[1]
        cap = data_list[2]
        city = data_list[3]
        
        if len(nameaddr) == 0:
            raise ValidationError("A name or address for your place is expected")
        
        if len(city) == 0:
            raise ValidationError("A city is expected")
        
        # trick: save a one space string to make the cap optional - FS
        if len(cap) == 0:
            data_list[2] = " "
        
        
        # strip all input fields
        for i in range(0, len(data_list)-1):
            data_list[i] = data_list[i].strip()
        
        return super(PlaceField, self).clean(data_list)

class ContactField(forms.MultiValueField):
    widget = ContactWidget

    def __init__(self, *args, **kw):
        fields = (
            forms.IntegerField(),
            forms.ChoiceField(choices=CONTACT_CHOICES,label=_('flavour')),
            forms.CharField(label=_('contact')),
            forms.BooleanField(label=_('preferred'))
        )
        super(ContactField, self).__init__(fields, *args, **kw)
    
    def compress(self, data_list):
        print("Compress a Contact Field, DL=",data_list)
        if data_list:
            curr_id = data_list[0]
            flavour = data_list[1]
            contact = data_list[2]
            is_preferred = data_list[3]

            curr_cont = ''
            if curr_id:
                curr_cont = Contact.objects.get(pk=curr_id)
                curr_cont.flavour = flavour
                curr_cont.value = contact
                curr_cont.is_preferred = is_preferred
            else:
                if (contact):
                    curr_cont = Contact(
                        flavour=flavour,value=contact,
                        is_preferred = is_preferred
                    )

            return curr_cont
        return ''
        
    def clean(self, value):
        print ("Contact to clean =", value)
        if value[1].lower() == 'email':
            validate_email(value[2])
        if value[1].lower() == 'phone':
            validate_phone(value[2])
        return super(ContactField,self).clean(value)
            

class MultiContactWidget(forms.MultiWidget):
    @property
    def size(self):
        return self.num_contacts

    def __init__(self, n, attrs=None):
#        print("Ricevuto n=%d" % n)
        widgets = []
        self.num_contacts = n
        for i in range(n):
            widgets.append(ContactWidget())

        super(MultiContactWidget, self).__init__(widgets, attrs)
#
    def decompress(self, value):
        print("Compress a MultiContactWidget. Value =", value)
        if value:
            #contact_id_set = value.split("::")[0:self.num_contacts]
            contact_id_set = value
            contacts = []
            for curr_id in contact_id_set:
                if curr_id.isdigit():
#                    print("Search pk=",curr_id)
                    contact_found = Contact.objects.filter(pk=curr_id)
                    print("Found=",contact_found)
                    if contact_found != None:
                        contacts.append(contact_found)
            
            print("All contacts=",contacts)
            return contacts
        else:
            return ''

        

class MultiContactField(forms.MultiValueField):
    widget = None

    def __init__(self, n, *args, **kw):
        fields = []

        for i in range(n):
            fields.append(ContactField())

        self.widget = MultiContactWidget(n)

        super(MultiContactField, self).__init__(fields, *args, **kw)

    def set_widget(self, n):
        self.widget = MultiContactWidget(n)

    def clean(self, value):
        print("Clean data=",value)
        email_found = False
        for currData in value:
            if currData[1] != None and currData[1].lower() == 'email' and currData[2].strip() != '':
                # at least one email contact -> OK
                email_found = True
                break
                
        if not email_found:
            # no email -> ValidationError
            raise forms.ValidationError("At least an email contact expected")
        
        return super(MultiContactField, self).clean(value)
#        return value
#
    def compress(self, data_list):
        print("Compress a MultiContactField, Data_List=",data_list)
        if self.widget == None:
            return
# TODO could we cut the data_list in case it's longer than widget size?
        if len(data_list) > self.widget.size:
            raise Exception("%d items expected, %d received" %
                (self.widget.size, len(data_list))
            )

        result = []
        #contact_id_list = [] # array('I')
        email_found = False
        
        # check there is one preferred contact per flavour
        # NB non-specified flavours are ignored
        preferred_missing = set()
        preferred_found = set()
             
        for curr_contact in data_list:
            if not curr_contact:
                continue

            result.append(curr_contact)
            email_found = email_found or (curr_contact.flavour.lower() == 
                "email")
            
            if curr_contact.is_preferred:
                preferred_found.add(curr_contact.flavour)
                if (curr_contact.flavour in preferred_missing):
                    preferred_missing.remove(curr_contact.flavour)
            elif not(curr_contact.flavour in preferred_found):
                # ! curr_contact.is_preferred & curr_contact.flavour not in preferred_found
                preferred_missing.add(curr_contact.flavour)
                

        if email_found == False:
            raise forms.ValidationError("Email contact expected but not found")

        if len(preferred_missing) > 0:
            raise forms.ValidationError("One preferred contact per flavour expacted. Missing preferred for: " + ','.join(preferred_missing) );
        
        #result = string.join(contact_id_list,"::")
        
        return result
