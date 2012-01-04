Questo progetto è l'esercizio di creazione di due form fields
che incorporano la logica di modelli (B,C) collegati ad un 
modello principale A.

Per realizzare l'esercizio è stato creato il progetto Django
`fooproj` e l'applicazione `people`. I modelli interessati
sono `Person` (modello A) che è collegato a:

* `Contact` (modello C) che incapsula la logica di un contatto (ad es: FAX 071123123123, o EMAIL a@a.com)
* `Place` (modello B) che incapsula la logica di un luogo (ad es: via tal dei tali, 60100 Ancona (AN), oppure "casa mia")

L'implementazione dei field è fatta nel file `people/lib/fields.py` e i field vengono
utilizzati nella form `PersonForm` implementata nell'admin interface `people/admin.py`.

Al momento della creazione del repository alcune cose sono state fatte,
di seguito gli esercizi che mancano per portare a termine l'attività:


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
  Più un campo (multiplo) contatti vuoto. 


