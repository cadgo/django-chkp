from .models import R80Users, MGMTServer
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import formset_factory

class MyLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                             'placeholder': 'Enter UserName'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                             'placeholder': 'Enter Password'}))

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


class RuleLayer(forms.Form):
    LayerForm = forms.CharField(label='Layer to Use', max_length=20,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

class RuleBasesForm(forms.Form):
    ActionChoice = (('Accept', 'Accept'), ('Drop', 'Drop'),)
    LogChoice = (('Log', 'Log'), ('Full Log', 'Full Log'),('Network Log', 'Network Log'), ('None', 'None'),)
    # LayerForm = forms.CharField(label='Layer to Use', max_length=20,
    #                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    RuleName = forms.CharField(label='Rule Name',max_length=20, strip=True,
                               widget = forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'RuleName'}))
    FWRuleOrigin = forms.ChoiceField(label='Src IP')
    FwRuleDst = forms.ChoiceField(label='Dst IP')
    #FWRulePort = forms.IntegerField(min_value=1, max_value=65525)
    FWRulePort = forms.ChoiceField(label='Port')
    ActionRule = forms.ChoiceField(label='Action', choices=ActionChoice)
    LogRule = forms.ChoiceField(label='Log', choices = LogChoice)
    #UsersFormChoice = forms.ChoiceField(label='Users', choices=UsersQuery)
    #MgmtFormChoice = forms.ChoiceField(label='SMSServer', choices=MgmtQuery)

    def __init__(self, tcplist, udplist, hostlists, networks, *args, **kwargs):
        #Validar que las listas vengan con información que no esten en cero
        super().__init__(*args, **kwargs)
        self.fields['FWRulePort'].choices = tcplist + udplist
        if hostlists == None:
            self.fields['FWRuleOrigin'].choices = networks
            self.fields['FwRuleDst'].choices = networks
        elif networks == None:
            self.fields['FWRuleOrigin'].choices = hostlists
            self.fields['FwRuleDst'].choices = hostlists
        else:
            self.fields['FWRuleOrigin'].choices = hostlists + networks
            self.fields['FwRuleDst'].choices = hostlists + networks

    # def __init__(self, tcplist, udplist, hostlists, networks, *args, **kwargs):
    #     #Validar que las listas vengan con información que no esten en cero
    #     super().__init__(*args, **kwargs)
    #     self.fields['FWRulePort'].choices = tcplist + udplist
    #     self.fields['FWRuleOrigin'].choices = hostlists + networks
    #     self.fields['FwRuleDst'].choices = hostlists + networks

MultiRulesForm = formset_factory(RuleBasesForm, min_num=1, extra=2, max_num=10)

class ChoseConsoleForm(forms.Form):
    #MgmtQuery = tuple(MGMTServer.objects.values_list('id', 'ServerIP'))
    MgmtFormChoice = forms.ChoiceField(label='SMSServer')

    def __init__(self, servers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['MgmtFormChoice'].choices = servers

class R80CreateHost(forms.Form):
    name = forms.CharField(label='Host Name', max_length=20)
    IPv4Address = forms.GenericIPAddressField(label='IP Address', protocol="IPv4")

    #Agregar init para que R80CreateHostNatHide, pueda ser validada, ya que necesitamos tomar de kwarfs name e IPv4Address
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

class R80CreateHostNatHide(R80CreateHost):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['Nat'] = forms.CharField(label='Nat Hide', initial='hide', widget=forms.HiddenInput())
        self.fields['SrcNat'] = forms.ChoiceField(label='Hide Nat', choices=(('behind GW', 'behind GW'),('IP Address', 'IP Address'),))
        self.fields['SrcIP'] = forms.CharField(label='Src NAT IP', initial='gateway')

class R80CreateHostNatStatic(R80CreateHost):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['NatIP'] = forms.GenericIPAddressField(label='Nated IP', protocol="IPv4")

class DummyJSR80CreateNatHide(forms.Form):
    SrcNat = forms.ChoiceField(label='Hide Nat', choices=(('behind GW', 'behind GW'),('IP Address', 'IP Address')))
    SrcIP = forms.CharField(label='Src NAT IP', initial='gateway')

class DummyJSR80CreateHostNatStatic(forms.Form):
    NatIP = forms.GenericIPAddressField(label='Nated IP', protocol="IPv4")

class R80CreateNet(forms.Form):
    name = forms.CharField(label='Net Name', max_length=20)
    IPv4NetAddress = forms.GenericIPAddressField(label='IP Address', protocol="IPv4")
    subnet = forms.IntegerField(label='subnet', initial=24 ,min_value=1, max_value=32)

class R80CreateNetNatHide(R80CreateNet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['Nat'] = forms.CharField(label='Nat Hide', initial='hide', widget=forms.HiddenInput())
        self.fields['SrcNat'] = forms.ChoiceField(label='Hide Nat', choices=(('behind GW', 'behind GW'),('IP Address', 'IP Address'),))
        self.fields['SrcIP'] = forms.CharField(label='Src NAT IP', initial='gateway')

class DummyJSR80CreateNetHide(forms.Form):
    SrcNat = forms.ChoiceField(label='Hide Nat', choices=(('behind GW', 'behind GW'),('IP Address', 'IP Address')))
    SrcIP = forms.CharField(label='Src NAT IP', initial='gateway')


class R80CreateNetNatStatic(R80CreateNet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['NatIP'] = forms.GenericIPAddressField(label='Nated IP', protocol="IPv4")

class DummyJSR80CreateNetNatStatic(forms.Form):
    NatIP = forms.GenericIPAddressField(label='Nated IP', protocol="IPv4")