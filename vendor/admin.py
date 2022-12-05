from django.contrib import admin
from vendor.models import Vendor

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'is_approved', 'created_at')
    list_display_links = ('user', 'vendor_name')         #when u click on user or vendorname u will get the above details

admin.site.register(Vendor, VendorAdmin)