import datetime
from django.utils.timezone import utc
from precoinr.apps.AccountManager.models import Account, AccountFund
from precoinr.apps.MerchantAdmin.models import Merchant
from precoinr.libs.BTC.BTCAccountManipulator import BtcAPIInterface
import logging

#ownerUserId= models.IntegerField(default=0)
#cardImage = models.ImageField(upload_to='AccountCards')
logger = logging.getLogger(__name__)
class AccountCreator:
    def createAccount(self, mrShort, ccType):
        newRandomPIN = "1234"

        newAcc = Account(accountType='PrePay', pinHash=newRandomPIN, creationTime=datetime.datetime.utcnow().replace(tzinfo=utc))
        newAcc.save()

        newFund = self.addCurencyToAccount(newAcc, ccType)

        if newFund!=None:
            try:
                if(newAcc.mainCCAddress==''):
                    newAcc.mainCCAddress=newFund.ccAdress
                newAcc.save()
            except ValueError:
                newAcc.delete()
                raise Exception('Could not create account!')

            return newAcc

        raise Exception('Could not create account!')

    def addCurencyToAccount(self, acc, ccType):

        #TODO: only if not yet present

        try:
            AccountFund.get(accountId=acc, currencyCode=ccType)
            logger.error("Account "+acc.accountName+' allready has fund of type '+ccType+'. Will not create one.')
            return None
        except:
            pass

        newFund = AccountFund(accountId=acc)

        if(ccType=='BTC'):
           # newAddress = BtcAPIInterface.createAccount()
            newAddress = '1JDZA1t7uXTTivp12inmkx5GKKiGcn53ud'
            newFund.fundAddress = newAddress
            newFund.currencyCode=ccType
            newFund.currencyType='Crypto'
        else:
            raise ValueError('No usable Crypto currency Type!!')

        newFund.save()

        return newFund