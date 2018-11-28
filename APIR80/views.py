from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models, forms
from . import tasks
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import redirect
from pathlib import Path
import json

class LoginIndex(generic.ListView):
    model = models.R80Users
    #template_name = 'APIR80/index.html'
    template_name = 'registration/login.html'



# # Create your views here.
# def index2(request):
#     print(request.user.is_authenticated)
#     if request.user.is_authenticated:
#         return render(request, 'APIR80/extend.html')
#     return render(request, 'APIR80/index.html')
#
# def extends(request):
#     if request.user.is_authenticated:
#         return render(request, 'APIR80/extend.html')
#     else:
#         return render(request, 'APIR80/index.html')


class AnsibleDemo2(LoginRequiredMixin, generic.ListView):
      template_name = 'APIR80/ansibledemo.html'
      login_url = '../../r80api/accounts/login/'
      model = models.MGMTServer
      form_class = forms.AnsibleSMSDeploy
      success_url = '/thanks/'
      redirect_field_name = 'redirect_to'

      def form_valid(self, form):
          return super().form_valid(form)

class RulesDemo(LoginRequiredMixin, View):
    template_name = 'APIR80/rulesdemo.html'
    login_url = '../../r80api/accounts/login/'
    form_class = forms.RuleBasesForm
    redirect_field_name = 'redirect_to'
    RulesDemoForms = {}
    ServerInfo = {'MgmtServerData': None, 'MgmtServerUser': None,
                  'MgmtObjects': None}

    #def __init__(self):
    #    self.RulesDemoForms['rulesform'] = self.form_class()
    #     #self.RulesDemoForms['R80UsersForm'] = forms.ModelsUsersAndMgmtServer()

    def __CheckFilesAndData(self):
        """"Si los archivos no existen los creamos y hacemos el Qery para llenarlo
        Si existen y tienen info, verifcamos que esta sea del ultima version si no lo actualizamos
        METER CLASE HIJA DE LA CHKPAPI (CheckPointEConnection) PARA VALIDAR POR EJEMPLO CUANDO NO HAYA OBJETOS EN TOTAL IGUAL A 0
        VALIDAR LOS TOTALES DE LOS OBJECTOS PARA IR POR TODOS DE UN JALON PARA QUE SOLO GENERE UN ARCHIVO EN BLANCO
        En el caso de los puertos tcp solo vamos por 217 arreglar eso a traves del wrapper para siempre ir por los totales.
        """
        conn = tasks.CheckPointAPI(self.ServerInfo['MgmtServerData'].ServerIP,
                                   self.ServerInfo['MgmtServerData'].MgmtPort)
        fileTCPPorts = Path(self.ServerInfo['MgmtObjects'].MGMTServerFilePathTCPPorts)
        fileUDPPorts= Path(self.ServerInfo['MgmtObjects'].MGMTServerFilePathUDPPorts)
        fileObjects = Path(self.ServerInfo['MgmtObjects'].MGMTServerFilePathNetObjects)
        fileNetworks = Path(self.ServerInfo['MgmtObjects'].MGMTServerFilePathNetworksObjects)
        #Si no existen los archivos
        print(fileUDPPorts)
        conn.ChkpLogin(self.ServerInfo['MgmtServerUser'].R80User, self.ServerInfo['MgmtServerUser'].R80Password)
        if not(fileTCPPorts.is_file() and fileObjects.is_file() \
                and fileUDPPorts.is_file() and fileNetworks.is_file()):
            #ENTRA CON TRUE
            fileTCPPorts.touch()
            fileObjects.touch()
            fileUDPPorts.touch()
            fileNetworks.touch()
            #tcpPorts = json.dumps(conn.ChkpShowServicesTCP())
            tcpPorts = json.dumps(conn.ChkpShowFullServicesTCP())
            udpPorts = json.dumps(conn.ChkpShowFullServicesUDP())
            fileTCPPorts.write_text(tcpPorts)
            fileUDPPorts.write_text(udpPorts)
            hosts = json.dumps(conn.ChkpShowFullHosts())
            fileObjects.write_text(hosts)
            networks = json.dumps(conn.ChkpShowFullNetworks())
            fileNetworks.write_text(networks)
        else:
            #Existen los archivos tenemos que verificar la ultima version de la API si no actualizarlos
            DBChkpVersion = self.ServerInfo['MgmtServerData'].LastPublishSession
            RemoteVersion = conn.ChkpShowLastPublishedSession()
            RemoteVersion = RemoteVersion['publish-time']['posix']
            #Si las versiones de Base de datos son distintas vamos por todo nuevamente
            if DBChkpVersion != RemoteVersion:
                print('Versiones diferentes actualizando la versiones')
                #tcpPorts = json.dumps(conn.ChkpShowServicesTCP())
                tcpPorts = json.dumps(conn.ChkpShowFullServicesTCP())
                udpPorts = json.dumps(conn.ChkpShowFullServicesUDP())
                fileTCPPorts.write_text(tcpPorts)
                fileUDPPorts.write_text(udpPorts)
                hosts = json.dumps(conn.ChkpShowFullHosts())
                fileObjects.write_text(hosts)
                networks = json.dumps(conn.ChkpShowFullNetworks())
                fileNetworks.write_text(networks)
                self.ServerInfo['MgmtServerData'].LastPublishSession = RemoteVersion
                self.ServerInfo['MgmtServerData'].save()
            else:
                print('Mismas versiones nada que modificar')
        conn.LogOutCheckPoint()

    def GetListTCPObjects(self):
        """"Validar que no tengan cero estos valores"""
        rdata =[]
        total = 0
        with open(self.ServerInfo['MgmtObjects'].MGMTServerFilePathTCPPorts) as f:
            data = json.load(f)
        total = data['total']
        if total == 0:
            return rdata.append(['',''])
        for i in range(total):
            # print(data['objects'][i]['name'])
            # print(data['objects'][i]['port'])
            rdata.append([data['objects'][i]['name'],'tcp:'+data['objects'][i]['port']])
        return rdata

    def GetListUDPObjects(self):
        """"Validar que no tengan cero estos valores"""
        rdata =[]
        total = 0
        with open(self.ServerInfo['MgmtObjects'].MGMTServerFilePathUDPPorts) as f:
            data = json.load(f)
        total = data['total']
        if total == 0:
            return rdata.append(['',''])
        for i in range(total):
            # print(data['objects'][i]['name'])
            # print(data['objects'][i]['port'])
            rdata.append([data['objects'][i]['name'],'udp:'+data['objects'][i]['port']])
        return rdata

    def GetListHostsObjects(self):
        """"Validar que no tengan cero estos valores"""
        rdata = []
        total = 0
        with open(self.ServerInfo['MgmtObjects'].MGMTServerFilePathNetObjects) as f:
            data = json.load(f)
        total = data['total']
        if total == 0:
            return rdata.append(['',''])
        for i in range(total):
            rdata.append([data['objects'][i]['name'],data['objects'][i]['ipv4-address']])
        return rdata


    def GetListNetworkObjects(self):
        #Solo procesa redes en IPv4 las de IPv6 las remueve
        """"Validar que no tengan cero estos valores"""
        rdata = []
        total = 0
        with open(self.ServerInfo['MgmtObjects'].MGMTServerFilePathNetworksObjects) as f:
            data = json.load(f)
        total = data['total']
        if total == 0:
            return rdata.append(['',''])
        print(data)
        for i in range(total):
            try:
                rdata.append([data['objects'][i]['name'],data['objects'][i]['subnet4']])
            except KeyError:
                continue
            #rdata.append([data['objects'][i]['name'], ['prueba']])
        return rdata

    def get(self, request, *args, **kwargs):
        MgmtServerToUse = request.GET.get('MgmtFormChoice')
        if MgmtServerToUse == None:
            return redirect('extends')
        MgmtServerToUse = int(MgmtServerToUse)
        self.ServerInfo['MgmtServerData'] = models.MGMTServer.objects.get(pk=MgmtServerToUse)
        self.ServerInfo['MgmtServerUser'] = models.R80Users.objects.get(UsersID=MgmtServerToUse)
        self.ServerInfo['MgmtObjects'] = models.MGMTServerObjects.objects.get(MGMTServerObjectsID=MgmtServerToUse)
        self.__CheckFilesAndData()
        return render(request, self.template_name, {'rulesform': self.form_class(self.GetListTCPObjects(), self.GetListUDPObjects(),
                                                                                 self.GetListHostsObjects(),
                                                                                 self.GetListNetworkObjects())})

    def post(self, request, *args, **kwargs):
        print(request.POST)
        form = self.form_class(data=request.POST, tcplist=self.GetListTCPObjects(), udplist=self.GetListUDPObjects(),hostlists=self.GetListHostsObjects(), networks=self.GetListNetworkObjects())
        if form.is_valid():
            print("Es valida")
            conn = tasks.CheckPointAPI(self.ServerInfo['MgmtServerData'].ServerIP,
                                       self.ServerInfo['MgmtServerData'].MgmtPort)
            conn.ChkpLogin(self.ServerInfo['MgmtServerUser'].R80User, self.ServerInfo['MgmtServerUser'].R80Password)
            conn.ChkpAddAccessLayer(request.POST.get('LayerForm'))
            conn.ChkpSetLayerDefaultRuleToAccept('Cleanup rule', request.POST.get('LayerForm'))
            conn.ChkpAddAccesRule(request.POST.get('LayerForm'),
                                  request.POST.get('RuleName'),
                                  request.POST.get('FWRuleOrigin'),
                                  request.POST.get('FwRuleDst'),
                                  request.POST.get('FWRulePort'),
                                  request.POST.get('ActionRule'),
                                  request.POST.get('LogRule'))
            conn.ChkpPublish()
            conn.LogOutCheckPoint()
        else:
            print("No es valida")
            SuspiciousOperation("Invalid request: not able to process the form")
        return render(request, self.template_name, {'rulesform': self.form_class(self.GetListTCPObjects(), self.GetListUDPObjects(),
                                                                                 self.GetListHostsObjects(),
                                                                                 self.GetListNetworkObjects())})


class AnsibleDemo(LoginRequiredMixin, View):
    template_name = 'APIR80/ansibledemo.html'
    login_url = '../../r80api/accounts/login/'
    form_class = forms.AnsibleSMSDeploy
    redirect_field_name = 'redirect_to'
    AnsibleForms = {}

    def __init__(self):
        self.AnsibleForms["formsms"] = self.form_class()
        self.AnsibleForms["formGWt"] = forms.AnsibleFWDeploy()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.AnsibleForms)

    def post(self, request, *args, **kwargs):
        if request.POST.get('FwDeployFormHidden') == 'True':
            #INTEGRAR VALIDACIONES DE REGEX PARA LAS IPS SI SE 1.1.1.1. LO TOMA COMO VALIDO
            print("DeployGW")
            form = forms.AnsibleFWDeploy(request.POST)
            if form.is_valid():
                print("Form Fw is OK")
                tasks.counttomil()
            else:
                SuspiciousOperation("Invalid request: no able to process the form")
        if request.POST.get('SMSDeployFormHidden') == 'True':
            print("DeploySMS")
            form = self.form_class(request.POST)
            if form.is_valid():
                print("Form SMSDeploy OK")
            else:
                SuspiciousOperation("Invalid request: no able to process the form")
        # form = self.form_class(request.POST)
        # print(request.POST)
        # if form.is_valid():
        #     print(request.POST)
        #     SmartCenterName = form.cleaned_data['SmartCenterName']
        #     IPAddress = form.cleaned_data['SubNetIPAddress']
        #     print(SmartCenterName + ' ' + IPAddress)
        #     return HttpResponse('/suscess/')
        return render(request, self.template_name, self.AnsibleForms)

# class AnsibleDemo(View):
#     from_class = forms.AnsibleFirewallDeploy

class extendsView(LoginRequiredMixin, View):
    template_name = 'APIR80/extend.html'
    login_url = '../../r80api/accounts/login/'
    form_class = forms.ChoseConsoleForm
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        print(request)
        return render(request, self.template_name, {'form': form})