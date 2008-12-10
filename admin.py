from django.contrib import admin

class AdminSite(admin.AdminSite):
    pass

site = AdminSite()