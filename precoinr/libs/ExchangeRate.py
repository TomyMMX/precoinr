import json
import urllib2
from decimal import Decimal
from precoinr.apps.MerchantAdmin.models import ExchangeRate
from datetime import datetime, timedelta
from django.utils.timezone import utc
from precoinr.libs.CustomExceptions import UnsuportedCurrency
from urllib2 import URLError
import logging

logger = logging.getLogger(__name__)

def getExchangeRate(c1, c2):

    eRate = 0
    getFromSource=False
    addToDb = False
    try:
        rate = ExchangeRate.objects.get(currencyFrom=c1, currencyTo=c2)

        timeSince = datetime.utcnow().replace(tzinfo=utc) - rate.timeRead
        if timeSince > timedelta(minutes=5):
            getFromSource=True
            eRate=rate.rate
        else:
            return rate.rate
    except:
        getFromSource=True
        addToDb=True


    t1=c1
    t2=c2

    try:
        if(c1=='BTC' or c2=='BTC'):
            lastPrice = Decimal(json.load(urllib2.urlopen('https://www.bitstamp.net/api/ticker/'))['last'])

            if(c1=='EUR' or c2=='EUR'):
                data = json.load(urllib2.urlopen('https://www.bitstamp.net/api/eur_usd/'))
                exchange=(Decimal(data['sell'])+Decimal(data['buy']))/2

                t1='BTC'
                t2='EUR'
                eRate = lastPrice/exchange
            else:
                raise UnsuportedCurrency(c1+'::'+c2)
        else:
            raise UnsuportedCurrency(c1+'::'+c2)
    except (URLError, ValueError) as e:
        logger.error('Could not get exchange rate: '+e.message)
        return eRate


    if addToDb:
        timeNow = datetime.utcnow().replace(tzinfo=utc)
        newRate = ExchangeRate(currencyFrom=t1, currencyTo=t2, rate=eRate, timeRead=timeNow)
        newRate.save()

        newRate2 = ExchangeRate(currencyFrom=t2, currencyTo=t1, rate=1/eRate, timeRead=timeNow)
        newRate2.save()

    if t1==c1 :
        return eRate
    else:
        return 1/eRate



