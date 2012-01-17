
from django.core.validators import RegexValidator
from django.utils.translation import ugettext, ugettext_lazy as _

import re

class PhoneValidator(RegexValidator):

    def __call__(self, value):
        return "ciao"

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
validate_phone = PhoneValidator(email_re, _(u'Enter a valid e-mail address.'), 'invalid')

