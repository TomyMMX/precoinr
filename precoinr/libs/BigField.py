from django.core import exceptions
from django.conf import settings
from django.db import connection
from django.db.models import fields
from django.utils.translation import ugettext as _

__version__ = "1.0"
__author__ = "Florian Leitner"

class BigIntegerField(fields.IntegerField):

    def db_type(self, connection):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE == 'postgres':
            return "bigint"
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigIntegerField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigAutoField(fields.AutoField):

    def db_type(self, connection):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint AUTO_INCREMENT"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE == 'postgres':
            return "bigserial"
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigAutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigForeignKey(fields.related.ForeignKey):

    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, BigAutoField) or
                (not connection.features.related_fields_match_type and
                     isinstance(rel_field, BigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return BigIntegerField().db_type()
        return rel_field.db_type()
