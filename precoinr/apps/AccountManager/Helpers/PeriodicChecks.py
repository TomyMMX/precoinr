from precoinr.libs.BTC.BTCAccountManipulator import BtcAPIInterface
from precoinr.apps.AccountManager.models import Account, AccountFund, Transaction
import bitcoinrpc
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from precoinr.apps.AccountManager.Helpers import FundDataHelpers
from django.db import IntegrityError, transaction
import logging
import sys

logger = logging.getLogger(__name__)

class BTCTransactionFinder:
    def SearchForNewBTCTransactions(self):

        '''
        logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                            datefmt="%Y-%m-%d %H:%M:%S",
                            format="[%(asctime)-15s] %(message)s")
        '''

        logger.info("Checking for new transaction data...")
        conn = bitcoinrpc.connect_to_local()
        for fund in AccountFund.objects.filter(currencyCode='BTC'):

            actualIn = BtcAPIInterface.getTotalReceived(conn, fund.fundAddress)

            transactions = BtcAPIInterface.getLastTransactions(conn, fund.fundAddress, fund.numTransactionsSeen)
            noSeen = self.WorkTroughNewTransactions(transactions, fund)

            if len(transactions)==noSeen:
                fund.numTransactionsSeen+=noSeen

            fund.totalIn=actualIn

            fund.save()

    def WorkTroughNewTransactions(self, transactions, fund):
        noSeen=0
        for tx in transactions:
                if tx.category=='receive':
                    thisTx = Transaction()
                    try:
                        thisTx = Transaction.objects.get(ccTxId=tx.txid)
                        noSeen = noSeen + 1
                    except ObjectDoesNotExist:
                        try:
                            with transaction.commit_on_success():
                                thisTx = Transaction()
                                thisTx.amount=tx.amount
                                thisTx.transactionType=tx.category
                                thisTx.ccTxId=tx.txid
                                thisTx.seenInWallet=True
                                thisTx.confirmations=tx.confirmations
                                thisTx.fundIdIn=fund.id
                                thisTx.timeStamp = datetime.utcfromtimestamp(tx.time).replace(tzinfo=utc)
                                thisTx.save()

                                FundDataHelpers.RecalculateFunds(thisTx)

                                noSeen = noSeen + 1
                                logger.info('NEW Deposit of '+tx.amount.__str__()+'on '+fund.fundAddress)
                        except Exception as e:
                            transaction.rollback()
                            logger.error('Could not commit incoming transaction on '+fund.fundAddress+': '+e.message)
                            return noSeen
                else:
                    logger.info('MOVE detected: '+tx.amount.__str__()+' from '+ fund.fundAddress)
                    noSeen = noSeen + 1

        return noSeen

    def CheckForNewConfirmations(self):
        conn = bitcoinrpc.connect_to_local()
        for loctx in Transaction.objects.filter(confirmations__lt = 100, transactionType='receive'):
            if AccountFund.objects.get(id=loctx.fundIdIn).currencyCode=='BTC':
                tx = conn.gettransaction(loctx.ccTxId)
                timeSince = datetime.utcnow().replace(tzinfo=utc) - loctx.timeStamp

                if loctx.confirmations != tx.confirmations:
                    try:
                        with transaction.commit_on_success():
                            old = loctx.confirmations
                            loctx.confirmations=tx.confirmations
                            FundDataHelpers.RecalculateFunds(loctx, old)
                            loctx.problemFlag = False
                            loctx.flagReason = ''
                            loctx.save()
                    except Exception as e:
                        transaction.rollback()
                        logger.error('Could not save confimration update on: '+loctx.id)


                elif timeSince > timedelta(hours=24) and loctx.confirmations < 50:
                    loctx.problemFlag = True
                    loctx.flagReason = timeSince.seconds/3600+' hours since seen. Only '+loctx.confirmations+' confirmations.'
                    logger.error(loctx.flagReason)
                    loctx.save()

