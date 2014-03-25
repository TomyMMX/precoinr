from django.db import models
from django.contrib.auth.models import User

class Merchant(models.Model):
    adminUser = models.OneToOneField(User)
    name = models.CharField(max_length=255)
    shortName = models.CharField(max_length=4)
    dateCreated = models.DateTimeField('date created')
    precoinrFee = models.IntegerField(default=100) #in percent of 1%
    holdInCC = models.BigIntegerField(default=100) #% of transaction to hold in Crypto currency

    def __unicode__(self):
        return self.name+"("+self.shortName+")"

class ExchangeRate(models.Model):
    currencyFrom = models.CharField(max_length=4)
    currencyTo = models.CharField(max_length=4)
    rate = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    timeRead = models.DateTimeField('timestamp')