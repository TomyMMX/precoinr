from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from precoinr.apps.AccountManager.models import Account, AccountFund, Transaction

admin.site.register(AccountFund)
admin.site.register(Transaction)
admin.site.register(Account)

class AccountInline(admin.StackedInline):
    model=Account
    can_delete = False
    verbose_name_plural = 'account'

class UserAdmin(UserAdmin):
    inlines = (AccountInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)