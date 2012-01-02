from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe


from people.models import Place

# define WIDGETS
class PlaceWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=(
                ('MC', 'Macerata'), ('AN', 'Ancona'),
                ('FM', 'Fermo'), ('AP', 'Ascoli Piceno')
            )),
        )
        super(PlaceWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        print("AAAA", value)
        if value:
            p = Place.objects.get(pk=value)
            return [p.name, p.zipcode, p.city, p.province]
            #return value.split(':::')[0:2]
        else:
            return ['','']    

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="placewidget">%s %s<br />%s %s %s %s %s %s</p>' % (
            _('Name:'), rendered_widgets[0], 
            _('ZIP:'), rendered_widgets[1],
            _('City:'), rendered_widgets[2],
            _('State:'), rendered_widgets[3],
        ))



class ContactWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        attrs.update({ 'style' : 'margin-right: 0.5em' })
        widget = (
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
        )
        super(ContactWidget, self).__init__(widget, attrs)

    def decompress(self, value):
        print(value)
        if value:
            return value.split(':::')[0:2]
        else:
            return ['','']    

# define FORMS
class PlaceField(forms.MultiValueField):
#    fields = ['address','city']
    widget = PlaceWidget

    def __init__(self, *args, **kw):
        fields = (
            forms.CharField(label=_("name")),
            forms.CharField(label=_("zip")),
            forms.CharField(label=_("city")),
            forms.ChoiceField(label=_("state")),
        )
        super(PlaceField, self).__init__(fields, *args, **kw)
    
    def compress(self, data_list):
        if data_list:
            return ':::'.join(data_list)
        else: 
            return ''

class ContactField(forms.MultiValueField):
    widget = ContactWidget

    def __init__(self, *args, **kw):
        fields = (
            forms.CharField(),
            forms.CharField(),
        )
        super(ContactField, self).__init__(fields, *args, **kw)
    
    def compress(self, data_list):
        print("data_list=%s" % data_list)
        if data_list:
            return ':::'.join(data_list)
        else: 
            return ''


class MultiContactField(forms.MultiValueField):

    def __init__(self, n, *args, **kw):

        fields = []
        for i in range(n):
            fields.append(ContactField())

        super(MultiContactField, self).__init__(fields, *args, **kw)

