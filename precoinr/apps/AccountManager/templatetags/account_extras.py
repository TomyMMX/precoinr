#coding: utf8
from django import template
register = template.Library()
from django.contrib.humanize.templatetags.humanize import intcomma

@register.filter
def currency(value):
    val=float(value)
    if val < 0.009 and val > -0.009:
        return ''

    dollars = round(val, 2)
    outStr="%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
    if val<0:
        return '-'+outStr
    else:
        return outStr

@register.filter
def cryptoCurrency(value):
    val=float(value)

    if val < 0.000009 and val > -0.000009:
        return ''

    dollars = round(val, 5)
    outStr="%s%s" % (intcomma(int(dollars)), ("%0.5f" % dollars)[-6:])

    if val<0:
        return '-'+outStr
    else:
        return outStr

