from people.models import Contact
from people.models import Place
from people.models import Person
from people.lib.fields import PlaceField
from people.lib.fields import ContactField


from django.contrib import admin
from django import forms

admin.site.register(Contact)
admin.site.register(Place)

#class ContactAdmin(admin.ModelAdmin):
#    fields = ['value','description']

#class PersonForm(forms.BaseModelForm): #LF
class PersonForm(forms.ModelForm): 
    #contact = ContactField()
    c = forms.ModelChoiceField(queryset=Contact.objects.all())
    place = PlaceField()
    t = forms.SplitDateTimeField(required=False)
    class Meta:
        model = Person

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm



admin.site.register(Person, PersonAdmin)
