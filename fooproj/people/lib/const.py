from django.utils.translation import ugettext as _

STATE_CHOICES = [
    ('AN', 'Ancona'),
    ('AP', 'Ascoli Piceno'),
    ('FM', 'Fermo'),
    ('MC', 'Macerata'),
    ('PU', 'Pesaro Urbino')
]

FLAVOUR_CHOICES = [
    ('email', _('email')),
    ('phone', _('phone')),
    ('phone2', _('phone2')),
    ('mobile', _('mobile')),
    ('mobile2',_('mobile2')),
    ('fax',_('fax')),
]
