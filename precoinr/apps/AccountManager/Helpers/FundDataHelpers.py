import bitcoinrpc
from precoinr.libs.BTC.BTCAccountManipulator import BtcAPIInterface
from precoinr.apps.AccountManager.models import Account, AccountFund
from precoinr.libs.CustomExceptions import UnsuportedCurrency, NonExistingCryptoCurency
from decimal import Decimal

def getAvailableFunds(acc, type, amount):
    try:
        fund = AccountFund.objects.get(currencyCode=type, accountId=acc)
    except:
        raise UnsuportedCurrency(type)

    if fund.currencyType == 'crypto':
        if fund.currencyCode=='BTC':
            #conn = bitcoinrpc.connect_to_local()

            availableFunds = fund.funds
            if amount > 4:
                availableFunds = fund.safeFunds

            return availableFunds
        else:
            raise NonExistingCryptoCurency(type)

    else:
        return fund.funds #here we have to trust our records

def RecalculateFunds(tx, prevConfirm=0):

    #if the transaction has an out fund it is internal or a withdraw.. so ve can update both funds
    if tx.fundIdOut!=0:
        f2 = AccountFund.objects.get(id=tx.fundIdOut)
        f2.funds-=Decimal(tx.amount)
        f2.safeFunds-=Decimal(tx.amount)
        f2.save()

    if tx.fundIdIn!=0:
        addFunds = False
        addSafeFunds = False
        if tx.transactionType == 'receive':
            if tx.confirmations>=3 and prevConfirm<3:
                addFunds=True
            if tx.confirmations>=50 and prevConfirm<50:
                addSafeFunds=True
        else:
            addFunds = True
            addSafeFunds = True

        f1 = AccountFund.objects.get(id=tx.fundIdIn)
        if addFunds:
            f1.funds+=Decimal(tx.amount)
        if addSafeFunds:
            f1.safeFunds+=Decimal(tx.amount)

        if addFunds or addSafeFunds:
            f1.save()




