from django.core.management.base import BaseCommand, CommandError
from precoinr.apps.AccountManager.Helpers.PeriodicChecks import BTCTransactionFinder
from precoinr.apps.AccountManager.Helpers.FundWithdrawer import Withdrawer

class Command(BaseCommand):
    def handle(self, *args, **options):
        bttf = BTCTransactionFinder()
        bttf.CheckForNewConfirmations()
        bttf.SearchForNewBTCTransactions()

        wd = Withdrawer()
        wd.DoManyWithdraw()
