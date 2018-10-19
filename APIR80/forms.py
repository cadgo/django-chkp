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


# class ModelsUsersAndMgmtServer(forms.Form):
#     UsersQuery = tuple(R80Users.objects.values_list('id', 'R80User'))
#     MgmtQuery = tuple(MGMTServer.objects.values_list('id', 'ServerIP'))
#     UsersFormChoice = forms.MultipleChoiceField(label='Users', widget=forms.Select, choices=UsersQuery)
#     MgmtFromChoice = forms.MultipleChoiceField(label='SMSServer', widget=forms.Select, choices=MgmtQuery)

class RuleBasesForm(forms.Form):
    ProtocolChoice = (('tcp', 'tcp'), ('udp', 'udp'),)
    ActionChoice = (('Accept', 'Accept'), ('Drop', 'Drop'),)
    LogChoice = (('Log', 'Log'), ('Full Log', 'Full Log'),('Network Log', 'Network Log'), ('None', 'None'),)
    LayerForm = forms.CharField(label='Layer to Use', max_length=20)
    RuleName = forms.CharField(label='rule name', max_length=20, strip=True)
    FWRuleOrigin = forms.ChoiceField(label='Src IP')
    FwRuleDst = forms.ChoiceField(label='Dst IP')
    #FWRulePort = forms.IntegerField(min_value=1, max_value=65525)
    FWRulePort = forms.ChoiceField(label='Port')
    ProtocolType = forms.ChoiceField(choices=ProtocolChoice)
    ActionRule = forms.ChoiceField(label='Action', choices=ActionChoice)
    LogRule = forms.ChoiceField(label='Log', choices = LogChoice)
    #UsersFormChoice = forms.ChoiceField(label='Users', choices=UsersQuery)
    #MgmtFormChoice = forms.ChoiceField(label='SMSServer', choices=MgmtQuery)

    def __init__(self, tcplist, hostlists, *args, **kwargs):
        #Validar que las listas vengan con información que no esten en cero
        super().__init__(*args, **kwargs)
        self.fields['FWRulePort'].choices = tcplist
        self.fields['FWRuleOrigin'].choices = hostlists
        self.fields['FwRuleDst'].choices = hostlists

class ChoseConsoleForm(forms.Form):
    #UsersQuery = tuple(R80Users.objects.values_list('id', 'R80User'))
    #MgmtQuery = tuple(MGMTServer.objects.values_list('id', 'ServerIP'))
    MgmtQuery = tuple(MGMTServer.objects.values_list('id', 'ServerIP'))
    MgmtFormChoice = forms.ChoiceField(label='SMSServer', choices=MgmtQuery)


