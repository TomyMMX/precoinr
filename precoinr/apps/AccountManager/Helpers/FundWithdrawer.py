from precoinr.apps.AccountManager.models import Account, AccountFund, Transaction
import uuid
from datetime import datetime
from django.utils.timezone import utc
from django.db import IntegrityError, transaction
from precoinr.libs.BTC.BTCAccountManipulator import BtcAPIInterface
from precoinr.apps.AccountManager.Helpers import FundDataHelpers
import logging

logger = logging.getLogger(__name__)

class Withdrawer:
    def DoManyWithdraw(self):
        #BTC
        precoinrAcc = Account.objects.get(accountName='precoinr')
        mainBtcFund = AccountFund.objects.get(accountId=precoinrAcc, currencyCode='BTC')
        notWithdrawn = Transaction.objects.filter(transactionType= 'withdraw', ccTxId='', fundIdIn= mainBtcFund.id)

        btcOutList = []
        for tx in notWithdrawn:
            btcOutList.append(tx)

        if len(btcOutList)>0:
            btcOutDict = {}
            totalAmount = 0
            for tx in btcOutList:
                btcOutDict[tx.withdrawAddress] = float(tx.amount-tx.precoinrFee)
                totalAmount += btcOutDict[tx.withdrawAddress]
            try:
                with transaction.commit_on_success():
                    fee = 0.00005
                    outTx = self.CreateSystemOutTransaction(mainBtcFund, totalAmount, fee)
                    outTx.save()

                    ccTxId = BtcAPIInterface.sendMany(mainBtcFund.fundAddress, btcOutDict)

                    outTx.ccTxId=ccTxId
                    outTx.save()

                    for t in btcOutList:
                        t.ccTxId=ccTxId
                        FundDataHelpers.RecalculateFunds(t)
                        t.save()

            except Exception as e:
                logger.error('Could not make system withdraw: '+e.message)
                transaction.rollback()


    def CreateSystemOutTransaction(self, fund, amount, fee):
        tx = Transaction()
        tx.amount = amount
        precoinrAcc = Account.objects.get(accountName='precoinr')
        tx.fundIdOut = AccountFund.objects.get(accountId=precoinrAcc, currencyCode=fund.currencyCode).id
        tx.precoinrFee = fee
        tx.transactionType= 'systemOut'
        tx.timeStamp = datetime.utcnow().replace(tzinfo=utc)
        tx.TxUUId = uuid.uuid4().__str__()
        tx.ccTxId=''

        return tx

    def WithdrawFunds(self, accName, amount, currencyCode, outAddress):

        acc = Account.objects.get(accountName=accName)

        #TODO: check fund avalability
        fund = AccountFund.objects.get(accountId= acc, currencyCode=currencyCode)

        if currencyCode=='BTC':
            self.CreateWithdrawTransaction(fund, amount, outAddress).save()
        else:
            raise Exception

    def CreateWithdrawTransaction(self, fund, amount, outAddress):
        tx = Transaction()
        tx.withdrawAddress = outAddress
        tx.amount = amount
        precoinrAcc = Account.objects.get(accountName='precoinr')
        tx.fundIdIn = AccountFund.objects.get(accountId=precoinrAcc, currencyCode=fund.currencyCode).id
        tx.fundIdOut = fund.id
        tx.precoinrFee = amount*5/1000
        tx.transactionType= 'withdraw'
        tx.timeStamp = datetime.utcnow().replace(tzinfo=utc)
        tx.TxUUId = uuid.uuid4().__str__()
        tx.ccTxId=''

        return tx