from django.core.management.base import BaseCommand, CommandError
from precoinr.apps.AccountManager.Helpers.PaymentHelper import Payment

class Command(BaseCommand):
    def handle(self, *args, **options):
        pmt = Payment()
        pmt.PayToMerchant('1KUU6exVPSDFtMgAgdDnN5Z1145eL7teah', 1, 0.01, 'EUR', 'BTC', 'TestPayment1')
