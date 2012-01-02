from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User
import const

# Create your models here.
class Contact(models.Model):
    """If is a contact, just a contact email or phone"""

    flavour = models.CharField(max_length=32, choices=const.CONTACT_CHOICES, default=const.EMAIL,verbose_name=_('flavour'))
    #flavour = models.CharField(max_length=32, verbose_name=_('flavour'))

    value = models.CharField(max_length=256,verbose_name=_('value'))
    is_preferred = models.BooleanField(default=False,verbose_name=_('preferred'))
    description = models.CharField(max_length=128, blank=True, default='',verbose_name=_('description'))

#    history = HistoricalRecords()

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __unicode__(self):
        return u"%(t)s: %(v)s" % {'t': self.flavour, 'v': self.value}

    def clean(self):
        self.flavour = self.flavour.strip()
# FS commentato perche` const non e` riconosciuto
#        if self.flavour not in map(lambda x: x[0], const.CONTACT_CHOICES):
#            raise ValidationError(_("Contact flavour MUST be one of %s" % map(lambda x: x[0],  const.CONTACT_CHOICES)))
        self.value = self.value.strip()
        self.description = self.description.strip()
        return super(Contact, self).clean()

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
        
    #Geolocation: do not use GeoDjango PointField here. 
    #We can make a separate geo application maybe in future
    lon = models.FloatField(null=True, blank=True,verbose_name=_('lon'))
    lat = models.FloatField(null=True, blank=True,verbose_name=_('lat'))

#    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        ordering = ('name', 'address', 'city')

    def __unicode__(self):

        rv = u"" 
#        if self.name or self.address:
#            rv += (self.name or self.address) + u", "
        if self.address:
            rv += self.address + u", "

        if self.zipcode:
            rv += u"%s " % self.zipcode

        rv += self.city.lower().capitalize()

        if self.province:
            rv += u" (%s)" % self.province.upper()

        return rv

    def clean(self):

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

        #TODO: Copy-on-write model
        # a) check if an already existent place with the same full address exist and in that case force update
        # b) if we are updating a Place --> detach it from other stuff pointing to it and clone 

        super(Place, self).save(*args, **kw)
        
    #----------------- Authorization API ------------------------#
    
    # Table-level CREATE permission    
    @classmethod
    def can_create(cls, user, context):
        # Who can create a new Place in a DES ?
        # Everyone belongs to the DES
        
        try:
            des = context['site']
        except KeyError:
            raise WrongPermissionCheck('CREATE', cls, context)
        else:
            # It's ok because only one DES is supported
            return not user.is_anonymous()
            # otherwhise it should be
            # return user in User.objects.filter(person__in=des.persons)
                
    # Row-level EDIT permission
    def can_edit(self, user, context):
        # Who can edit details of an existing place in a DES ?
        # (note that places can be shared among GASs)
        # * DES administrators
        # * User that created the place
        # * User who has updated it. How he can do it? 
        #   If a User try to create a new place with the same parameters
        #   of an already existent one, he updates the place
        allowed_users =  self.des.admins | self.created_by | self.updaters
        return user in allowed_users
        
    # Row-level DELETE permission
    def can_delete(self, user, context):
        # Who can delete an existing place from a DES ?
        # (note that places can be shared among GASs)
        # * DES administrators
        # * User that created the place
        # * User who has updated it. How he can do it? see can_edit above
        allowed_users =  self.des.admins | self.created_by | self.updaters
        return user in allowed_users       
                
    #-----------------------------------------------------#

#@economic_subject
class Person(models.Model): #, PermissionResource):
    """
    A Person is an anagraphic record of a human being.
    It can be a User or not.
    """

    name = models.CharField(max_length=128,verbose_name=_('Name'))
    surname = models.CharField(max_length=128,verbose_name=_('Surname'))
    display_name = models.CharField(max_length=128, blank=True,verbose_name=_('Display name'))

    place = models.ForeignKey(Place,verbose_name=_('place'))
    contact_set = models.ManyToManyField('Contact', null=True, blank=True,verbose_name=_('contacts'))

    # Leave here ssn, but do not display it
    ssn = models.CharField(max_length=128, unique=True, editable=False, blank=True, null=True, help_text=_('Write your social security number here'),verbose_name=_('Social Security Number'))
#    contact_set = models.ManyToManyField('Contact', null=True, blank=True,verbose_name=_('contacts'))
#    user = models.OneToOneField(User, null=True, blank=True,verbose_name=_('User'))
    user = models.CharField(max_length=100)
#    address = models.ForeignKey('Place', null=True, blank=True,verbose_name=_('main address'))
    address = models.CharField(max_length=100)
    website = models.URLField(verify_exists=True, blank=True, verbose_name=_("web site"))

#    accounting = AccountingDescriptor(PersonAccountingProxy)
#    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("people")
        ordering = ('name',)

    def __unicode__(self):
        rv = self.display_name or u'%(name)s %(surname)s' % {'name' : self.name, 'surname': self.surname}
        return rv

    def report_name(self):
        return u'%(name)s %(surname)s' % {'name' : self.name, 'surname': self.surname}

    def clean(self):
        self.name = self.name.strip().lower().capitalize()
        self.surname = self.surname.strip().lower().capitalize()
        self.display_name = self.display_name.strip()
        if not self.ssn:
            self.ssn = None
        else:
            self.ssn = self.ssn.strip().upper()

        return super(Person, self).clean()
    
    @property
    def uid(self):
        """
        A unique ID (an ASCII string) for ``Person`` model instances.
        """
        return self.urn.replace('/','-')
    
    @property
    def parent(self):
        return self.des

    @property
    def icon(self):
        return self.avatar or super(Person, self).icon

    ## START Resource API
    # Note that all the following methods return a QuerySet
    
    @property
    def persons(self):
        return Person.objects.filter(pk=self.pk)

    @property
    def person(self):
        return self

    @property
    def gasmembers(self):
        #TODO UNITTEST
        """
        GAS members associated to this person;
        to each of them corresponds a membership of this person in a GAS.        
        """
        return self.gasmember_set.all()
    
    @property
    def gas_list(self):
        #TODO UNITTEST
        """
        All GAS this person belongs to
        (remember that a person may be a member of more than one GAS).
        """ 
        from gasistafelice.gas.models import GAS
        gas_pks = set(member.gas.pk for member in self.gasmembers)
        return GAS.objects.filter(pk__in=gas_pks)
    
    @property
    def des_list(self):
        #TODO UNITTEST
        """
        All DESs this person belongs to 
        (either as a member of one or more GAS or as a referrer for one or more suppliers in the DES).         
        """
        from gasistafelice.des.models import DES
        des_set = set([gas.des for gas in self.gas_list])
        return DES.objects.filter(pk__in=[obj.pk for obj in des_set])
    
    @property
    def des(self):
        from gasistafelice.des.models import Siteattr
        return Siteattr.get_site()
    
    @property
    def pacts(self):
        # TODO: what pacts are associated to a Person ?
        pass
    
    @property
    def suppliers(self):
        #TODO UNITTEST
        """
        A person is related to:
        1) suppliers for which he/she is a referrer
        2) suppliers who have signed a pact with a GAS he/she belongs to
        """
        from gasistafelice.supplier.models import Supplier
        # initialize the return QuerySet 
        qs = Supplier.objects.none()
        
        #add the suppliers who have signed a pact with a GAS this person belongs to
        for gas in self.gas_list:
            qs = qs | gas.suppliers
        
        # add the suppliers for which this person is an agent
        referred_set = set([sr.supplier for sr  in self.supplieragent_set])
        qs = qs | Supplier.objects.filter(pk__in=[obj.pk for obj in referred_set])
        
        return qs
        
    
    @property
    def orders(self):
        #TODO UNITTEST
        """
        A person is related to:
        1) supplier orders opened by a GAS he/she belongs to
        2) supplier orders for which he/she is a referrer
        3) order to suppliers for which he/she is a referrer
        
        """

        from gasistafelice.gas.models import GASSupplierOrder
                
        # initialize the return QuerySet 
        qs = GASSupplierOrder.objects.none()
        
        #add the supplier orders opened by a GAS he/she belongs to
        for gas in self.gas_list:
            qs = qs | gas.orders
        
        return qs
        
    
    @property
    def deliveries(self):
        #TODO UNITTEST
        """
        A person is related to:
        1) delivery appointments for which this person is a referrer
        2) delivery appointments associated with a GAS he/she belongs to
        """
        from gasistafelice.gas.models import Delivery
        # initialize the return QuerySet
        qs = Delivery.objects.none()    
        # add  delivery appointments for which this person is a referrer   
        for member in self.gasmembers:
            qs = qs | member.delivery_set.all()
        # add  delivery appointments associated with a GAS he/she belongs to
        for gas in self.gas_list:
            qs = qs | gas.deliveries
                                
        return qs
    
    @property
    def withdrawals(self):
        #TODO UNITTEST
        """
        A person is related to:
        1) withdrawal appointments for which this person is a referrer
        2) withdrawal appointments associated with a GAS he/she belongs to
        """
        from gasistafelice.gas.models import Withdrawal
        # initialize the return QuerySet
        qs = Withdrawal.objects.none()    
        # add  withdrawal appointments for which this person is a referrer   
        for member in self.gasmembers:
            qs = qs | member.withdrawal_set.all()
        # add  withdrawal appointments associated with a GAS he/she belongs to
        for gas in self.gas_list:
            qs = qs | gas.withdrawals
                                
        return qs  
    
    
    ## END Resource API    
    
    #-----------------------------------------------------#

    @property
    def username(self):
        if self.user:
            return self.user.username
        else:
            return ugettext("has not an account in the system")

