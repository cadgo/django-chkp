from django.contrib import admin
from .models import *
from django import forms


# Register your models here.
class ChoiceInline(admin.TabularInline):
    model = MGMTServer
# Register your models here.

class MGMTServerAdminPortal(admin.ModelAdmin):
    list_display = ('MgmtR80Name','ServerIP', 'Description', 'MgmtR80ApiVersion')

class R80UsersForm(forms.ModelForm):
    R80Password = forms.CharField(widget=forms.PasswordInput)

class R80UsersAdmin(admin.ModelAdmin):
    form = R80UsersForm
    fieldset = ('UsersID', 'R80User', 'R80Password')

class MGMTServerObjectsAdmin(admin.ModelAdmin):
    list_display = ('MGMTServerObjectsID', 'MGMTServerFilePathTCPPorts')

class MGMTServerObjectsAdminObjects(admin.ModelAdmin):
    list_display = ('MGMTServerObjectsNetworksID', 'MGMTServerFilePathNetObjects')

admin.site.register(MGMTServer, MGMTServerAdminPortal)
admin.site.register(R80Users, R80UsersAdmin)
admin.site.register(MGMTServerObjects, MGMTServerObjectsAdmin)