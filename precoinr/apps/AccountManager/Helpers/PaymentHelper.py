from precoinr.libs.BTC.BTCAccountManipulator import BtcAPIInterface
from precoinr.apps.AccountManager.models import Account, AccountFund, Transaction

from precoinr.apps.MerchantAdmin.models import Merchant
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from precoinr.libs.CustomExceptions import NonExistingCryptoCurency, NonExistingFiatCurency, \
                                           DifferenceBetweenCCandFiatTooLarge, InsufficientFunds, \
                                           CouldNotCommitPayment
from precoinr.apps.AccountManager.Helpers import FundDataHelpers
from django.db import IntegrityError, transaction
import uuid
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentData:
    acc = Account()
    mrc = Account()
    precoinrFee = int
    keepInCrypto = int
    payAmount = float
    payType = str
    requestAmount = float
    requestType = str
    exchangeRate = float
    posId = str
    timestamp = datetime
    txUUId = str
    actualExchangeAmount=float
    actualAmount=float

class Payment:
    def PayToMerchant(self, accName, merchantId, requestAmount, requestType, payType, posTxId):
        exchangeRate = self.getExchangeRate(payType, requestType)#TODO: get the exchange rate that was sent to merchant
        payAmount = float(requestAmount)/float(exchangeRate)

        merchant = Merchant.objects.get(id=merchantId)

        data = PaymentData()
        data.acc = Account.objects.get(accountName=accName)
        data.mrc = Account.objects.get(ownerUser=merchant.adminUser)

        data.keepInCrypto= merchant.holdInCC
        data.precoinrFee= merchant.precoinrFee

        availableFunds = FundDataHelpers.getAvailableFunds(data.acc, payType, payAmount)
        if availableFunds<payAmount:
            raise InsufficientFunds('Need :'+payAmount.__str__()+', Have: '+availableFunds.__str__())

        data.payAmount=payAmount
        data.payType=payType
        data.requestAmount=requestAmount
        data.requestType=requestType
        data.exchangeRate=exchangeRate
        data.posId=posTxId #so the merchant can tie this transaction to a sale
        data.timestamp = datetime.utcnow().replace(tzinfo=utc)
        data.txUUId=uuid.uuid4().__str__()

        self.CreateNeededTransactions(data)

    def CreateNeededTransactions(self, data):
        try:
            with transaction.commit_on_success():
                #Transaction 1: User PC OUT, Merchant PC IN
                data.actualAmount=data.payAmount
                t1 = self.CreateTransaction('pay', data)
                t1.save()

                #Transaction 2: Merchant Fee OUT, Precoinr Fee IN
                data.actualAmount=data.payAmount*float(data.precoinrFee)/10000
                t2 = self.CreateTransaction('fee', data)
                t2.save()

                FundDataHelpers.RecalculateFunds(t1)
                FundDataHelpers.RecalculateFunds(t2)

        except Exception as e:
            transaction.rollback()
            raise CouldNotCommitPayment('')

        if data.keepInCrypto<100:
            try:
                with transaction.commit_on_success():
                    #Transaction 3
                    #Merchant PC Part - > precoinr

                    data.actualAmount = data.payAmount - data.payAmount*float(data.keepInCrypto)/100
                    exchangeAmount = data.actualAmount * data.exchangeRate
                    data.actualExchangeAmount=exchangeAmount
                    t3 = self.CreateTransaction('exchangeOUT', data)
                    t3.save()

                    #Transaction 3
                    #Precoinr AC for part @ exchangeRate -> Merchant
                    data.actualAmount = exchangeAmount
                    t4 = self.CreateTransaction('exchangeIN', data)
                    t4.save()

                    FundDataHelpers.RecalculateFunds(t3)
                    FundDataHelpers.RecalculateFunds(t4)
            except Exception as e:
                transaction.rollback()

    def CreateTransaction(self, type, data):
        tx = Transaction()
        tx.amount = data.actualAmount

        if type == 'pay':
            tx.fundIdIn = AccountFund.objects.get(accountId=data.mrc, currencyCode=data.payType).id
            tx.fundIdOut = AccountFund.objects.get(accountId=data.acc, currencyCode=data.payType).id
            tx.precoinrFee = tx.amount*float(data.precoinrFee)/10000
            tx.exchangeAmount=data.requestAmount
            tx.exchangeCode=data.requestType
            tx.exchangeRate=data.exchangeRate

        elif type == 'fee':
            precoinrAcc = Account.objects.get(accountName='precoinr')
            tx.fundIdIn = AccountFund.objects.get(accountId=precoinrAcc, currencyCode=data.payType).id
            tx.fundIdOut = AccountFund.objects.get(accountId=data.mrc, currencyCode=data.payType).id

        elif type == 'exchangeOUT':
            precoinrAcc = Account.objects.get(accountName='precoinr')
            tx.fundIdIn = AccountFund.objects.get(accountId=precoinrAcc, currencyCode=data.payType).id
            tx.fundIdOut = AccountFund.objects.get(accountId=data.mrc, currencyCode=data.payType).id
            tx.exchangeAmount=data.actualExchangeAmount
            tx.exchangeCode=data.requestType
            tx.exchangeRate=data.exchangeRate

        elif type == 'exchangeIN':
            precoinrAcc = Account.objects.get(accountName='precoinr')
            tx.fundIdIn = AccountFund.objects.get(accountId=data.mrc, currencyCode=data.requestType).id
            tx.fundIdOut = AccountFund.objects.get(accountId=precoinrAcc.id, currencyCode=data.requestType).id

        tx.transactionType= type
        tx.timeStamp = data.timestamp
        tx.TxUUId = data.txUUId

        return tx

    def getExchangeRate(self, ccType, fiatType):
        if not ccType == 'BTC': #add as the support expands
            raise NonExistingCryptoCurency(ccType)
        if not fiatType== 'EUR':
            raise NonExistingFiatCurency(fiatType)

        if ccType==fiatType:
            return 1

        if ccType=='BTC':
            if fiatType=='EUR':
                return 100
            else:
                raise NonExistingFiatCurency(fiatType)
        else:
            raise NonExistingCryptoCurency(ccType)
