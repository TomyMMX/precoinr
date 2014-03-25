#coding: utf8
from django.contrib.auth.models import User
from precoinr.apps.AccountManager.models import Account, AccountFund, Transaction
from decimal import Decimal
from operator import attrgetter
from itertools import chain

def createUserTransactionList(user, showUnconfirmed=False, shoOnlyUnconfirmed = False):
    displayTxList = []
    userFundIds = AccountFund.objects.filter(accountId=user.account.id).values('id')
    fundIds = []
    for fid in userFundIds:
        fundIds.append(fid['id'])
    inList = Transaction.objects.filter(fundIdOut__in=fundIds)
    outList = Transaction.objects.filter(fundIdIn__in=fundIds)
    allTxList = sorted(
        chain(inList, outList),
        key=attrgetter('timeStamp'))
    total = {}
    total['EUR'] = 0
    total['BTC'] = 0
    for tx in allTxList:
        txData = {}

        addTx = True
        confirmed = True
        if tx.transactionType == 'receive':
            txData['type'] = 'deposit'
            if tx.confirmations<3:
                confirmed = False
        elif tx.transactionType=='withdraw':
            txData['type'] = 'withdraw'
            if tx.ccTxId=='':
                confirmed=False
        elif tx.transactionType == 'pay':
            txData['type'] = 'payment'
        elif tx.transactionType == 'fee':
            txData['type'] = 'fee'
        elif tx.transactionType == 'exchangeOUT':
            txData['type'] = 'exchange'
        else:#when we add transaction types we will hanlde this
            txData['type'] = 'NA'
            addTx = False

        if not showUnconfirmed and not confirmed:
            addTx = False

        if showUnconfirmed and shoOnlyUnconfirmed and not confirmed:
            addTx = True
        elif showUnconfirmed and shoOnlyUnconfirmed and confirmed:
            addTx = False

        if addTx:
            txData['timestamp'] = tx.timeStamp

            if tx.precoinrFee != 0:
                txData['precoinrfee'] = round(tx.precoinrFee * 1000, 5)
            else:
                txData['precoinrfee'] = 0

            mCns = round(tx.amount * 1000, 5)

            if txData['type'] == 'payment' and tx.fundIdIn in fundIds:
                mCns -= txData['precoinrfee']

            if tx.fundIdOut in fundIds:
                txData['coins'] = 0 - mCns
            else:
                txData['coins'] = mCns

            txData['coinsSign'] = ''
            fId = tx.fundIdOut
            if fId == 0:
                fId += tx.fundIdIn

            ccode = AccountFund.objects.get(id=fId).currencyCode
            if ccode == 'BTC':
                txData['coinsSign'] = 'mɃ'

            if tx.exchangeRate != 0:
                txData['exRate'] = tx.exchangeRate
            else:
                txData['exRate'] = 0

            txData['amount'] = 0
            txData['amountSign'] = ''
            txData['value'] = 0
            txData['valueSign'] = ''

            if (tx.exchangeCode == 'EUR'):
                if txData['type'] == 'payment':
                    txData['valueSign'] = '€'
                    txData['value'] = round(tx.exchangeAmount, 2)
                else:
                    if tx.fundIdOut in fundIds:
                        txData['amount'] = round(tx.exchangeAmount, 2)
                    else:
                        txData['amount'] = 0 - round(tx.exchangeAmount, 2)

                    txData['amountSign'] = '€'

            if user.is_superuser:
                pass
                #if txData['type'] == 'exchange':
                #    txData['amountEUR']= 0-txData['amountEUR']
                #    totalEUR+=2*txData['amountEUR']
            elif user.groups.filter(name='MerchantUser').count():
                if txData['type'] == 'fee':
                    addTx = False
            elif user.groups.filter(name='NormalUser').count():
                if txData['type'] == 'fee':
                    addTx = False
                if txData['type'] == 'payment':
                    txData['precoinrfee'] = 0

            if addTx:
                total['EUR'] += txData['amount']
                total['BTC'] += txData['coins']
                displayTxList.append(txData)
    data = {'transactions': displayTxList, 'total': total}
    return data


