from .models import R80Users
from django import forms


class R80UsersForm(forms.ModelForm):
    R80Password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = R80Users
        fields = ['UsersID', 'R80User', 'R80Password']


class AnsibleSMSDeploy(forms.Form):
    SmartCenterName = forms.CharField(label='SMS Name', max_length=20)
    SubNetIPAddress = forms.GenericIPAddressField(label='IP Address', protocol="IPv4")


class AnsibleFWDeploy(forms.Form):
    FirewallName = forms.CharField(label='Fw Name', max_length=20)
    FwIP = forms.GenericIPAddressField(label='IP Address', protocol="IPv4")
