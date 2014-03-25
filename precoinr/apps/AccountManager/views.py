#coding: utf8
from numpy.core.numerictypes import allTypes
from django.http import HttpResponse
from precoinr.apps.AccountManager.models import Account, AccountFund, Transaction
from precoinr.apps.AccountManager.Helpers.AccountCreator import AccountCreator
from precoinr.apps.AccountManager.Helpers.PaymentHelper import Payment
from precoinr.apps.AccountManager.Helpers.FundWithdrawer import Withdrawer
from precoinr.apps.AccountManager.Helpers.TransactionDataHelper import createUserTransactionList
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from precoinr.libs import ExchangeRate
from precoinr.apps.AccountManager.Helpers.PeriodicChecks import BTCTransactionFinder

from math import ceil
@login_required
def index(request):

    #fdh = BTCTransactionFinder()
    #fdh.CheckForNewConfirmations()

    #pmt = Payment()
    #pmt.PayToMerchant('1KUU6exVPSDFtMgAgdDnN5Z1145eL7teah', 1, 0.01, 'EUR', 'BTC', 'TestPayment1')

    #wd = Withdrawer()
    #wd.WithdrawFunds('1KUU6exVPSDFtMgAgdDnN5Z1145eL7teah', 0.0001, 'BTC', '12at3mFdtghPzz2ESTtGPktYKNw5JFWmEr')

    funds = AccountFund.objects.filter(accountId=request.user.account)
    fundList = []

    sumFiat = 0
    bal = 0
    BTCFundAdress = ''
    for f in funds:
        if(f.currencyCode!='EUR'):
            fundList.append(f)

            f.FiatValue=f.funds*ExchangeRate.getExchangeRate('BTC', 'EUR')
            sumFiat+=f.FiatValue

        if(f.currencyCode=='BTC'):
            bal=f.funds
            f.coinprefix = 'm'
            BTCFundAdress = f.fundAddress

    transactions = createUserTransactionList(request.user, True, True)

    deposit = {}
    deposit['BTC'] = {}
    deposit['BTC']['Address'] = BTCFundAdress
    deposit['BTC']['QrString'] = 'bitcoin:'+BTCFundAdress

    data =  {'funds':fundList, 'sum':sumFiat, 'activeTransactions' : transactions,
             'depositData': deposit }

    return render_to_response('Account.html', addCommonData(request, data))

@login_required
def history(request):
    #userid = request.user.id
    user = request.user

    data = createUserTransactionList(user)

    return render_to_response('History.html', addCommonData(request, data))

def withdraw(request):
    return HttpResponse('bu')

def create(request, merchant_short):
    ac = AccountCreator()
    newAcc = ac.createAccount(merchant_short, 'BTC')
    return HttpResponse(newAcc.mainCCAddress)

def addCommonData(request, data):
    fund = AccountFund.objects.get(accountId=request.user.account, currencyCode='BTC')
    data['balance']= str(Decimal(fund.funds*1000).quantize( Decimal(10) ** -5))
    return data