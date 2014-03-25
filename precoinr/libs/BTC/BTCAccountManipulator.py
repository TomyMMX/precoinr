import bitcoinrpc

class BtcAPIInterface:
    @staticmethod
    def createAccount():
        conn = bitcoinrpc.connect_to_local()
        newAddress = conn.getnewaddress()
        conn.setaccount(newAddress, newAddress)
        return newAddress

    @staticmethod
    def getTotalReceived(conn, accountName):
        rec = conn.getreceivedbyaccount(accountName, 1)
        return rec

    @staticmethod
    def getLastTransactions(conn, accountName, start):
        transactions = conn.listtransactions(accountName, 20, start)
        return transactions

    @staticmethod
    def getAccountFunds(conn, accountName, noConfirms):
        transactions = conn.getbalance(accountName, noConfirms) #three confirmations to actually add money to account balance
        return transactions

    @staticmethod
    def moveFunds(conn, accountOut, accounIn, amount, txUUId):
        transactions = conn.move(accountOut, accounIn, amount, 3, txUUId)
        return transactions


    @staticmethod
    def sendMany(fromAcc, toDict):
        conn = bitcoinrpc.connect_to_local()
        conn.walletpassphrase('hoho2theWORLD', 10)
        txId = conn.sendmany(fromAcc, toDict, 50)
        conn.walletlock()

        return txId





