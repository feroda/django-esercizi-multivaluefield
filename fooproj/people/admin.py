from django.utils.translation import ugettext as _

from django.db import transaction

from people.models import Contact
from people.models import Place
from people.models import Person
from people.lib.fields import PlaceField
from people.lib.fields import ContactField
from people.lib.fields import MultiContactField

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_field


from django.contrib import admin
from django import forms

admin.site.register(Contact)
admin.site.register(Place)

#--------------------------------------------------------------------------------

class PersonForm(forms.ModelForm):

    place = make_ajax_field(Person, 
        label = _("address"),
        model_fieldname='place',
        channel='placechannel', 
        help_text=_("Search for place by name, by address, or by city")
    )
    contact_set = MultiContactField(n=3,label=_('Contacts'))

#    def __init__(self, request, *args, **kw):
    def __init__(self,  *args, **kw):
        super(PersonForm, self).__init__(*args, **kw)
        model = self._meta.model
#        autoselect_fields_check_can_add(self,model,request.user)

    @transaction.commit_on_success
    def save(self, *args, **kw):
        """Save related objects and then save model instance"""

        for contact in self.cleaned_data['contact_set']:
            if contact.value:
                contact.save()
            elif contact.pk:
                self.cleaned_data['contact_set'].remove(contact)

        return super(PersonForm, self).save(*args, **kw)

    class Meta:
        model = Person
        fields = (
            'name', 'surname', 'contact_set', 'place'
        )
        gf_fieldsets = [(None, { 
            'fields' : (
                ('name', 'surname'),  
                'address', 'contact_set'),  
        })]


##class ContactAdmin(admin.ModelAdmin):
##    fields = ['value','description']
#
##class PersonForm(forms.BaseModelForm): #LF
#class PersonForm(forms.ModelForm): 
#    """
#    * Esercizio 1: salvataggio Place(). 
#      Ricevere i dati nella form e recuperare il Place relativo.
#      In caso di modifica salvare l'istanza. 
#      Reimplementare il metodo save() del modello Place secondo quanto
#      documentato in Place.save (models.py)
#
#    * Esercizio 2: messa a punto ContactField(). 
#    Recupero e renderizzazione di un solo contatto.
#    Salvataggio dell'istanza come per Place.
#    Select widget per il flavour (Fisso, Cell, Email, Fax, Fisso2, Cell2)
#    
#    * Esercizio 3: messa a punto di MultiContactField().
#    Modifica di 3 contatti in un unico form.
#
#    * Esercizio 4: 
#    Impostare l'email come obbligatoria.
#    Proporre direttamente la select con Email, Fisso, Cell.
#    Piu` un campo (multiplo) contatti vuoto). 
#    """
#
#    #place = PlaceField()
#    place = make_ajax_field(Person,'place','place',help_text="Search for place by name")
#    contact_set = MultiContactField(n=3,label=_('Contacts'))
#
##    def __init__(self, *args, **kwargs):
##        print("Dentro PersonForm")
##        return super(PersonForm,self).__init__(args, kwargs)
#
#    class Meta:
#        model = Person
#

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm    

admin.site.register(Person, PersonAdmin)
