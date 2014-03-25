from django.db import models
from django.contrib.auth.models import User
from precoinr.libs.BigField import BigAutoField
from decimal import Decimal

class Account(models.Model):
    ownerUser = models.OneToOneField(User)
    accountType = models.CharField(max_length=13)
    accountName = models.CharField(max_length=40, unique=True)
    pinHash = models.CharField(max_length=50)
    wasOnline = models.BooleanField(default=False)
    creationTime = models.DateTimeField('creation time')
    cardImage = models.ImageField(upload_to='AccountCards')
    def __unicode__(self):
        return self.accountName

class AccountFund(models.Model):
    accountId = models.ForeignKey(Account)
    fundAddress = models.CharField(max_length=40, unique=True)
    funds = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    safeFunds = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    totalIn = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    numTransactionsSeen = models.IntegerField(default=0)
    currencyCode = models.CharField(max_length=4)
    currencyType = models.CharField(max_length=8)

    #optional
    problemFlag = models.BooleanField(default=False)
    flagReason = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.currencyCode+"::"+self.fundAddress+": "+self.funds.__str__()

    def fundsString(self):
        return str(Decimal(self.funds*1000).quantize( Decimal(10) ** -5))

class AccountFundCheck(models.Model): #checks all transactions since the last check and sees if funds agree
    fundId = models.ForeignKey(AccountFund)
    funds = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    safeFunds = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    lastUsedTxTimeStamp = models.DateTimeField('usedTxTimeStamp')
    timeStamp = models.DateTimeField('timestamp')

class AccountModifyAction(models.Model):
    accountId = models.ForeignKey(Account)
    requestIp = models.IPAddressField()
    userId = models.IntegerField(default=0) #if logged in
    timeStamp = models.DateTimeField('timestamp')
    actionDescription = models.TextField()

class Transaction(models.Model):
    id = BigAutoField(primary_key=True)
    fundIdOut = models.IntegerField(default=0) #no incoming fund when it is a Deposit
    fundIdIn =models.IntegerField(default=0) #no in fund when SystemOut
    transactionType = models.CharField(max_length=13)
    TxUUId = models.CharField(max_length=100) #id of the request.. set when evaluated. For payment, Withdrawal, CC purchase
    amount = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    precoinrFee = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    timeStamp = models.DateTimeField('timestamp')
    requestIp = models.CharField(max_length=20)

    #optional
    problemFlag = models.BooleanField(default=0)
    flagReason = models.CharField(max_length=255)

    #set later
    seenInWallet = models.BooleanField(default=False) #was seen in our wallet

    #crypto data
    ccTxId = models.CharField(max_length=100) #for deposits and withdrawals, payments and ccBuys are internal
    confirmations = models.IntegerField(default=0) #no confirmations in the BlockChain

    #Withdrawal data
    withdrawAddress = models.CharField(max_length=34)

    #Deposit data
    addressFrom = models.CharField(max_length=34)

    #PaymentData
    posTxId = models.CharField(max_length=255)

    #Exchange data
    exchangeAmount = models.DecimalField(default=0, max_digits=20, decimal_places=9)
    exchangeCode = models.CharField(max_length=4)
    exchangeRate = models.DecimalField(default=0, max_digits=20, decimal_places=9)

    def __unicode__(self):
        return self.transactionType+": "+self.amount.__str__()+self.getCurencyType()
    def getCurencyType(self):
        return self.fundId.currencyCode

    def amountString(self):
        outStr = str(Decimal(self.amount*1000).quantize( Decimal(10) ** -5))

        return outStr+'m'



