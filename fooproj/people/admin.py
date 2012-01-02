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
    Più un campo (multiplo) contatti vuoto). 
    """

    #contact = ContactField()
    # LF: questo è qui per prova
    # c = forms.ModelChoiceField(queryset=Contact.objects.all())
    place = PlaceField()
    # LF: questo è qui per prova
    # t = forms.SplitDateTimeField(required=False)
    class Meta:
        model = Person

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm



admin.site.register(Person, PersonAdmin)
