from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User
import const

# Create your models here.
class Contact(models.Model):
    """If is a contact, just a contact email or phone"""

    flavour = models.CharField(max_length=32, choices=const.CONTACT_CHOICES, default=const.EMAIL,verbose_name=_('flavour'))
    value = models.CharField(max_length=256,verbose_name=_('value'))
    is_preferred = models.BooleanField(default=False,verbose_name=_('preferred'))
    description = models.CharField(max_length=128, blank=True, default='',verbose_name=_('description'))

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __unicode__(self):
        return u"%(t)s: %(v)s" % {'t': self.flavour, 'v': self.value}

    def clean(self):
        self.flavour = self.flavour.strip()
        if self.flavour not in map(lambda x: x[0], const.CONTACT_CHOICES):
            raise ValidationError(_("Contact flavour MUST be one of %s" % map(lambda x: x[0],  const.CONTACT_CHOICES)))
        self.value = self.value.strip()
        self.description = self.description.strip()
        return super(Contact, self).clean()

    def save(self, *args, **kw):
        #TODO: Copy-on-write model
        # a) check if an already existent place with the same full address exist and in that case force update
        # b) if we are updating a Contact --> remove pk and save, so clone it!
        # (a garbage collector will find unused places and remove them)

        equals_found = Contact.objects.filter(flavour=self.flavour,
            value=self.value,is_preferred=self.is_preferred,
            description=self.description)

        if len(equals_found) > 0:
            self.pk = equals_found[0].pk
        elif self.pk != None:
            # we are updating an object
            self.pk = None # forget the pk, so it will be saved a as copy(clone)

        super(Contact, self).save(*args, **kw)

class Place(models.Model): #, PermissionResource):
    """Places should be managed as separate entities for various reasons:
    * among the entities arising in the description of GAS' activities,
    there are several being places or involving places,
    so abstracting this information away seems a good thing;
    * in the context of multi-GAS (retina) orders,
    multiple delivery and/or withdrawal locations can be present.
    """

    name = models.CharField(max_length=128, blank=True, help_text=_("You can avoid to specify a name if you specify an address"),verbose_name=_('name'))
    description = models.TextField(blank=True,verbose_name=_('description'))

    # QUESTION: add place type from CHOICE (HOME, WORK, HEADQUARTER, WITHDRAWAL...)     
    # ANSWER: no place type here. It is just a point in the map
    address = models.CharField(max_length=128, blank=True,verbose_name=_('address'))

    #zipcode as a string: see http://stackoverflow.com/questions/747802/integer-vs-string-in-database
    zipcode = models.CharField(verbose_name=_("Zip code"), max_length=128, blank=True)

    city = models.CharField(max_length=128,verbose_name=_('city'))
    province = models.CharField(max_length=2, help_text=_("Insert the province code here (max 2 char)"),verbose_name=_('province')) 
        
    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        ordering = ('name', 'address', 'city')



    def __unicode__(self):

        rv = u"" 
        if self.name or self.address:
            rv += (self.name or self.address) + u", "
#        if self.address:
#            rv += self.address + u", "

        if self.zipcode:
            rv += u"%s " % self.zipcode

        rv += self.city.lower().capitalize()

        if self.province:
            rv += u" (%s)" % self.province.upper()

        return rv

    def clean(self):
        print ("SELF = ", self)

        self.name = self.name.strip().lower().capitalize()
        self.address = self.address.strip().lower().capitalize()

        #TODO: we should compute city and province starting from zipcode using local_flavor in forms
        self.city = self.city.lower().capitalize()
        self.province = self.province.upper()

        self.zipcode = self.zipcode.strip()
        if self.zipcode:
            try:
                int(self.zipcode)
            except ValueError:
                raise ValidationError(_("Wrong ZIP CODE provided"))

        self.description = self.description.strip()

        return super(Place, self).clean()

    def save(self, *args, **kw):

        #LF: In questo punto e` necessario implementare la nuova creazione su modifica

        #TODO: Copy-on-write model
        # a) check if an already existent place with the same full address exist and in that case force update
        # b) if we are updating a Place --> remove pk and save, so clone it!
        # (a garbage collector will find unused places and remove them)

        equals_found = Place.objects.filter(name=self.name,
            address=self.address,zipcode=self.zipcode,
            city=self.city,province=self.province)

        if len(equals_found) > 0:
            self.pk = equals_found[0].pk
        elif self.pk != None:
            # we are updating an object
            self.pk = None # forget the pk, so it will be saved a as copy(clone)

        super(Place, self).save(*args, **kw)
        

class Person(models.Model):
    """
    A Person is an anagraphic record of a human being.
    It can be a User or not.
    """

    name = models.CharField(max_length=128,verbose_name=_('Name'))
    surname = models.CharField(max_length=128,verbose_name=_('Surname'))
    display_name = models.CharField(max_length=128, blank=True,verbose_name=_('Display name'))

    place = models.ForeignKey(Place,verbose_name=_('place'))
    contact_set = models.CharField(max_length=128,null=True,blank=True,verbose_name=_('contacts'))
#    contact_set = models.ManyToManyField('Contact', null=True, blank=True,verbose_name=_('contacts'))
#    contact_set = models.ForeignKey(Contact, verbose_name=_('contact'))

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("people")
        ordering = ('name',)

    def __unicode__(self):
        rv = self.display_name or u'%(name)s %(surname)s' % {'name' : self.name, 'surname': self.surname}
        return rv

    def clean(self):
        self.name = self.name.strip().lower().capitalize()
        self.surname = self.surname.strip().lower().capitalize()
        self.display_name = self.display_name.strip()
        #if not self.ssn:
        #    self.ssn = None
        #else:
        #    self.ssn = self.ssn.strip().upper()

        return super(Person, self).clean()
    
