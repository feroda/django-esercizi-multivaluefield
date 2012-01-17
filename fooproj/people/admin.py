from django.utils.translation import ugettext as _

from people.models import Contact
from people.models import Place
from people.models import Person
from people.lib.fields import PlaceField
from people.lib.fields import ContactField
from people.lib.fields import MultiContactField

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_field
from ajax_select.fields import autoselect_fields_check_can_add

from django.contrib import admin
from django import forms
from django.db import transaction

admin.site.register(Contact)
admin.site.register(Place)

#class ContactAdmin(admin.ModelAdmin):
#    fields = ['value','description']

#class PersonForm(forms.BaseModelForm): #LF
class PersonForm(forms.ModelForm): 
    """
    * Esercizio 1: salvataggio Place(). 
      Ricevere i dati nella form e recuperare il Place relativo.
      In caso di modifica salvare l'istanza. 
      Reimplementare il metodo save() del modello Place secondo quanto
      documentato in Place.save (models.py)

    * Esercizio 2: messa a punto ContactField(). 
    Recupero e renderizzazione di un solo contatto.
    Salvataggio dell'istanza come per Place.
    Select widget per il flavour (Fisso, Cell, Email, Fax, Fisso2, Cell2)
    
    * Esercizio 3: messa a punto di MultiContactField().
    Modifica di 3 contatti in un unico form.

    * Esercizio 4: 
    Impostare l'email come obbligatoria.
    Proporre direttamente la select con Email, Fisso, Cell.
    Piu` un campo (multiplo) contatti vuoto). 
    """

    #place = PlaceField()
    place = make_ajax_field(Person, model_fieldname='place',
        channel='place', help_text="Search for place by name"
    )
    contact_set = MultiContactField(n=3,label=_('Contacts'))

    def __init__(self, *args, **kwargs):
#        print("Dentro PersonForm")
        super(PersonForm,self).__init__(*args, **kwargs)
        self.fields['place'].widget.attrs.update({
            'style' : 'width:400px'
        })
        if self.instance.pk:
            c = self.instance.contact_set.count()
            if c >= 3:
                self.fields['contact_set'].set_widget(c+1)

    class Meta:
        model = Person

class PersonAdmin(admin.ModelAdmin):

    form = PersonForm    

    def get_form(self, request, obj=None, **kwargs):
        form = super(PersonAdmin,self).get_form(request,obj,**kwargs)
        autoselect_fields_check_can_add(form,self.model,request.user)
        return form

    @transaction.commit_on_success
    def save_model(self, request, obj, form, change):
        """Save related objects and then save model instance"""

        for contact in form.cleaned_data['contact_set']:
            contact.save()

        super(PersonAdmin, self).save_model(request, obj, form, change)


admin.site.register(Person, PersonAdmin)
