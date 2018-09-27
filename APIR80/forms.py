from .models import R80Users, MGMTServer
from django import forms


class R80UsersForm(forms.ModelForm):
    R80Password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = R80Users
        fields = ['UsersID', 'R80User', 'R80Password']


class AnsibleSMSDeploy(forms.Form):
    SmartCenterName = forms.CharField(label='SMS Name', max_length=20)
    SubNetIPAddress = forms.GenericIPAddressField(label='IP Address', protocol="IPv4")
    SMSDeployFormHidden = forms.CharField(widget=forms.HiddenInput, initial='True')


class AnsibleFWDeploy(forms.Form):
    FirewallName = forms.CharField(label='Fw Name', max_length=20)
    FwIP = forms.GenericIPAddressField(label='IP Address', protocol="IPv4")
    FwDeployFormHidden = forms.CharField(widget=forms.HiddenInput, initial='True')


class RuleBasesForm(forms.Form):
    ProtocolChoice = (('tcp', 'TCP'), ('udp', 'UDP'),)
    LayerForm = forms.CharField(label='Layer to Use', max_length=20)
    RuleName = forms.CharField(label='rule name', max_length=20, strip=True)
    FWRuleOrigin = forms.GenericIPAddressField(label='Src IP', protocol="IPv4")
    FwRuleDst = forms.GenericIPAddressField(label='Dst IP', protocol="IPv4")
    FWRulePort = forms.IntegerField(min_value=1, max_value=65525)
    ProtocolType = forms.MultipleChoiceField(widget=forms.Select,choices=ProtocolChoice)


class ModelsUsersAndMgmtServer(forms.Form):
    UsersQuery = tuple(R80Users.objects.values_list('id', 'R80User'))
    MgmtQuery = tuple(MGMTServer.objects.values_list('id', 'ServerIP'))
    UsersFormChoice = forms.MultipleChoiceField(label='Users', widget=forms.Select, choices=UsersQuery)
    MgmtFromChoice = forms.MultipleChoiceField(label='SMSServer', widget=forms.Select, choices=MgmtQuery)

