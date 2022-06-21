from django.contrib import admin

from .models import PurchaseConfirmation


class PurchaseConfirmationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PurchaseConfirmation, PurchaseConfirmationAdmin)
