from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models, forms
from . import tasks
from .models import R80Users, MGMTServer
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import redirect
from pathlib import Path
from django.views.generic.edit import FormView
import json

class LoginIndex(generic.ListView):
    model = models.R80Users
    #template_name = 'APIR80/index.html'
    template_name = 'registration/login.html'


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
    form_class = forms.MultiRulesForm
    form_layer = forms.RuleLayer
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
            return None
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
            return None
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
            return None
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
            return None
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
        tcpObjects = self.GetListTCPObjects()
        udpObjects = self.GetListUDPObjects()
        hostObjects = self.GetListHostsObjects()
        networkObjects = self.GetListNetworkObjects()
        if hostObjects == None and networkObjects == None:
            print('No objects')
            return render(request, self.template_name, {'noobjects': 'yes'})
        if hostObjects == None:
            return render(request, self.template_name,
                          {'rulesform': self.form_class(form_kwargs={'tcplist': tcpObjects, 'udplist': udpObjects,
                                                                     'hostlists': None,
                                                                     'networks': networkObjects}),'layer': self.form_layer()})
        elif networkObjects == None:
            return render(request, self.template_name,
                          {'rulesform': self.form_class(form_kwargs={'tcplist': tcpObjects, 'udplist': udpObjects,
                                                                     'hostlists': hostObjects,
                                                                     'networks': None}),'layer': self.form_layer()})
        return render(request, self.template_name, {'rulesform': self.form_class(form_kwargs={'tcplist': tcpObjects,'udplist':udpObjects,
                                                                                 'hostlists': hostObjects, 'networks': networkObjects}),
                                                                                    'layer': self.form_layer()})

    def post(self, request, *args, **kwargs):
        """
        Falta agregar el formset factory para ser procesado por nuestro post
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        layerform = self.form_layer(data=request.POST)
        form = self.form_class(data=request.POST, form_kwargs={'tcplist':self.GetListTCPObjects(),
                                                               'udplist':self.GetListUDPObjects(),
                                                               'hostlists':self.GetListHostsObjects(),
                                                               'networks':self.GetListNetworkObjects()})
        if form.is_valid() and layerform.is_valid():
            print("****************************Es valida******************************")
            print(request.POST)
            ### PONER LAS VALIDACIONES DEL FORMULARIO CON LA METADATA
            TotalForms = int(request.POST.get("form-TOTAL_FORMS"))
            MinNumForms = int(request.POST.get("form-MIN_NUM_FORMS"))
            MaxNumForms = int(request.POST.get("form-MAX_NUM_FORMS"))
            if TotalForms < MinNumForms:
                SuspiciousOperation("Invalid request: not able to process the form")
            if TotalForms > MaxNumForms:
                SuspiciousOperation("Invalid request: not able to process the form")
            layer = layerform.cleaned_data["LayerForm"]
            conn = tasks.CheckPointAPI(self.ServerInfo['MgmtServerData'].ServerIP,
                                        self.ServerInfo['MgmtServerData'].MgmtPort)
            conn.ChkpLogin(self.ServerInfo['MgmtServerUser'].R80User, self.ServerInfo['MgmtServerUser'].R80Password)
            conn.ChkpAddAccessLayer(layer)
            conn.ChkpSetLayerDefaultRuleToAccept('Cleanup rule', layer)
            cdata=form.cleaned_data
            cdata.reverse()
            print(cdata)
            for rules in cdata:
                conn.ChkpAddAccesRule(layer,
                                      rules['RuleName'],
                                      rules['FWRuleOrigin'],
                                      rules['FwRuleDst'],
                                      rules['FWRulePort'],
                                      rules['ActionRule'],
                                      rules['LogRule'])
            conn.ChkpPublish()
            conn.LogOutCheckPoint()
        else:
            print("No es valida")
            SuspiciousOperation("Invalid request: not able to process the form")
        return render(request, self.template_name, {'rulesform': self.form_class(form_kwargs={'tcplist':self.GetListTCPObjects(),
                                                                                              'udplist':self.GetListUDPObjects(),
                                                                                              'hostlists':self.GetListHostsObjects(),
                                                                                              'networks':self.GetListNetworkObjects()}),
                                                                                                'layer': self.form_layer()})

    def get1(self, request, *args, **kwargs):
        MgmtServerToUse = request.GET.get('MgmtFormChoice')
        if MgmtServerToUse == None:
            return redirect('extends')
        MgmtServerToUse = int(MgmtServerToUse)
        self.ServerInfo['MgmtServerData'] = models.MGMTServer.objects.get(pk=MgmtServerToUse)
        self.ServerInfo['MgmtServerUser'] = models.R80Users.objects.get(UsersID=MgmtServerToUse)
        self.ServerInfo['MgmtObjects'] = models.MGMTServerObjects.objects.get(MGMTServerObjectsID=MgmtServerToUse)
        self.__CheckFilesAndData()
        tcpObjects = self.GetListTCPObjects()
        udpObjects = self.GetListUDPObjects()
        hostObjects = self.GetListHostsObjects()
        networkObjects = self.GetListNetworkObjects()
        if hostObjects == None and networkObjects == None:
            print('No objects')
            return render(request, self.template_name, {'noobjects': 'yes'})
        if hostObjects == None:
            render(request, self.template_name, {'rulesform': self.form_class(tcpObjects, udpObjects,
                                                                              None, networkObjects)})
        elif networkObjects == None:
            render(request, self.template_name, {'rulesform': self.form_class(tcpObjects, udpObjects,
                                                                              hostObjects, None)})
        return render(request, self.template_name, {'rulesform': self.form_class(tcpObjects,udpObjects,
                                                                                 hostObjects, networkObjects)})
        #return render(request, self.template_name, {'rulesform': self.form_class(self.GetListTCPObjects(), self.GetListUDPObjects(),
                                                                                 #self.GetListHostsObjects(),
                                                                                 #self.GetListNetworkObjects())})
    def post1(self, request, *args, **kwargs):
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
        MgmtQuery = tuple(MGMTServer.objects.values_list('id', 'ServerIP'))
        form = self.form_class(MgmtQuery)
        print(request)
        return render(request, self.template_name, {'form': form})

class CreateHostView(LoginRequiredMixin, FormView):
    template_name = 'APIR80/createhost.html'
    form_class= forms.R80CreateHost
    success_url = "extends/rulesdemo/"
    MgmtServer= None
    dummyhideNatJS = forms.DummyJSR80CreateNatHide
    dummystaticNatJS = forms.DummyJSR80CreateHostNatStatic

    def get(self, request):
        MgmtServerToUse = request.GET.get('MgmtFormChoice')
        if MgmtServerToUse == None:
            return redirect('extends')
        CreateHostView.MgmtServer = int(MgmtServerToUse)
        print(CreateHostView.MgmtServer)
        #self.MgmtServerToUse = models.MGMTServer.objects.get(pk=int(MgmtServerToUse))
        #self.ChkpLoginInfo = models.R80Users.objects.get(UsersID=MgmtServerToUse)
        return render(request, self.template_name, {'form': self.form_class(),
                                                    'dummyhide': self.dummyhideNatJS(),
                                                    'dummyStatic': self.dummystaticNatJS(),
                                                    'posturl': 'createhost'})

    def post(self, request):
        print(request.POST)
        if request.POST.get('NatRadio') == 'NoNat':
            print("No Nateamos")
            form = self.form_class(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                ipv4host = form.cleaned_data['IPv4Address']
                print("name {}, ipv4host {} post {}".format(CreateHostView.MgmtServer,
                                                            name, ipv4host))
                serverInfo = models.MGMTServer.objects.get(pk=CreateHostView.MgmtServer)
                LoginInfo = models.R80Users.objects.get(UsersID=CreateHostView.MgmtServer)
                conn = tasks.CheckPointAPI(serverInfo.ServerIP, serverInfo.MgmtPort)
                conn.ChkpLogin(LoginInfo.R80User, LoginInfo.R80Password)
                conn.ChkpCreateHost(name, ipv4host)
                conn.ChkpPublish()
                conn.LogOutCheckPoint()
                return render(request, self.template_name, {'form': self.form_class(), 'status': 'close'})
        if request.POST.get('NatRadio') == 'NatHide':
            print("Generamos un Nat Hide")
            form = forms.R80CreateHostNatHide(data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                ipv4host = form.cleaned_data['IPv4Address']
                srcnat = form.cleaned_data['SrcNat']
                print("name {}, ipv4host {} post {}".format(CreateHostView.MgmtServer,
                                                            name, ipv4host))
                serverInfo = models.MGMTServer.objects.get(pk=CreateHostView.MgmtServer)
                LoginInfo = models.R80Users.objects.get(UsersID=CreateHostView.MgmtServer)
                conn = tasks.CheckPointAPI(serverInfo.ServerIP, serverInfo.MgmtPort)
                conn.ChkpLogin(LoginInfo.R80User, LoginInfo.R80Password)
                if srcnat == 'behind GW':
                    print('Nat behindGW')
                    conn.ChkpCreateHost(name, ipv4host, 'hide')
                    conn.ChkpPublish()
                    conn.LogOutCheckPoint()
                elif srcnat == 'IP Address':
                    print('Nat IP Address')
                    srcip = form.cleaned_data['SrcIP']
                    conn.ChkpCreateHost(name, ipv4host, 'hide', srcip)
                    conn.ChkpPublish()
                    conn.LogOutCheckPoint()
                else:
                    conn.LogOutCheckPoint()
                    return render(request, self.template_name, {'form': self.form_class()})
                return render(request, self.template_name, {'form': self.form_class(), 'status': 'close'})
        if request.POST.get('NatRadio') == 'StaticNat':
            print("Generamos un Nat Estatico")
            form = forms.R80CreateHostNatStatic(data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                ipv4host = form.cleaned_data['IPv4Address']
                staticIP = form.cleaned_data['NatIP']
                serverInfo = models.MGMTServer.objects.get(pk=CreateHostView.MgmtServer)
                LoginInfo = models.R80Users.objects.get(UsersID=CreateHostView.MgmtServer)
                conn = tasks.CheckPointAPI(serverInfo.ServerIP, serverInfo.MgmtPort)
                conn.ChkpLogin(LoginInfo.R80User, LoginInfo.R80Password)
                conn.ChkpCreateHost(name, ipv4host, 'static', staticIP)
                conn.ChkpPublish()
                conn.LogOutCheckPoint()
                return render(request, self.template_name, {'form': self.form_class(), 'status': 'close'})
        return render(request, self.template_name, {'form': self.form_class(),
                                                            'dummyhide': self.dummyhideNatJS(),
                                                            'dummyStatic': self.dummystaticNatJS(),
                                                            'posturl': 'createhost'})

class CreateNetworkView(LoginRequiredMixin, FormView):
    template_name = 'APIR80/createhost.html'
    form_class = forms.R80CreateNet
    success_url = "extends/rulesdemo/"
    dummyhideNatJS = forms.DummyJSR80CreateNetHide
    dummystaticNatJS = forms.DummyJSR80CreateNetNatStatic
    MgmtServer = None

    def get(self, request):
        MgmtServerToUse = request.GET.get('MgmtFormChoice')
        if MgmtServerToUse == None:
            return redirect('extends')
        CreateHostView.MgmtServer = int(MgmtServerToUse)
        print(CreateHostView.MgmtServer)
        return render(request, self.template_name, {'form': self.form_class(),
                                                    'dummyhide': self.dummyhideNatJS(),
                                                    'dummyStatic': self.dummystaticNatJS(),
                                                    'posturl': 'createnetwork'})

    def post(self, request):
        print(request.POST)
        if request.POST.get('NatRadio') == 'NoNat':
            print("No Nateamos")
            form = self.form_class(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                #ipv4host = form.cleaned_data['IPv4NetAddress']
                ipv4NetAddress = form.cleaned_data['IPv4NetAddress']
                subnet = form.cleaned_data['subnet']
                print("name {}, ipv4NetAddress {} mask {}".format(CreateHostView.MgmtServer,
                                                            name, ipv4NetAddress, subnet))
                serverInfo = models.MGMTServer.objects.get(pk=CreateHostView.MgmtServer)
                LoginInfo = models.R80Users.objects.get(UsersID=CreateHostView.MgmtServer)
                conn = tasks.CheckPointAPI(serverInfo.ServerIP, serverInfo.MgmtPort)
                conn.ChkpLogin(LoginInfo.R80User, LoginInfo.R80Password)
                conn.ChkpCreateNetwork(name, ipv4NetAddress, subnet)
                conn.ChkpPublish()
                conn.LogOutCheckPoint()
                return render(request, self.template_name, {'form': self.form_class(), 'status': 'close'})
        if request.POST.get('NatRadio') == 'NatHide':
            print("Generamos un Nat Hide")
            form = forms.R80CreateNetNatHide(data=request.POST)
            print(form.is_valid())
            if form.is_valid():
                name = form.cleaned_data['name']
                #ipv4host = form.cleaned_data['IPv4Address']
                ipv4NetAddress = form.cleaned_data['IPv4NetAddress']
                subnet = form.cleaned_data['subnet']
                srcnat = form.cleaned_data['SrcNat']
                print("name {}, ipv4NetAddress {} post {}".format(CreateHostView.MgmtServer,
                                                                name, ipv4NetAddress))
                serverInfo = models.MGMTServer.objects.get(pk=CreateHostView.MgmtServer)
                LoginInfo = models.R80Users.objects.get(UsersID=CreateHostView.MgmtServer)
                conn = tasks.CheckPointAPI(serverInfo.ServerIP, serverInfo.MgmtPort)
                conn.ChkpLogin(LoginInfo.R80User, LoginInfo.R80Password)
                if srcnat == 'behind GW':
                    print('Nat behindGW')
                    conn.ChkpCreateNetwork(name, ipv4NetAddress, subnet, 'hide')
                    conn.ChkpPublish()
                    conn.LogOutCheckPoint()
                elif srcnat == 'IP Address':
                    print('Nat IP Address')
                    srcip = form.cleaned_data['SrcIP']
                    conn.ChkpCreateNetwork(name, ipv4NetAddress, subnet, 'hide', srcip)
                    conn.ChkpPublish()
                    conn.LogOutCheckPoint()
                else:
                    conn.LogOutCheckPoint()
                    return render(request, self.template_name, {'form': self.form_class()})
                return render(request, self.template_name, {'form': self.form_class(), 'status': 'close'})
        if request.POST.get('NatRadio') == 'StaticNat':
            print("Generamos un Nat Estatico")
            form = forms.R80CreateNetNatStatic(data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                #ipv4host = form.cleaned_data['IPv4Address']
                ipv4NetAddress = form.cleaned_data['IPv4NetAddress']
                staticIP = form.cleaned_data['NatIP']
                subnet = form.cleaned_data['subnet']
                serverInfo = models.MGMTServer.objects.get(pk=CreateHostView.MgmtServer)
                LoginInfo = models.R80Users.objects.get(UsersID=CreateHostView.MgmtServer)
                conn = tasks.CheckPointAPI(serverInfo.ServerIP, serverInfo.MgmtPort)
                conn.ChkpLogin(LoginInfo.R80User, LoginInfo.R80Password)
                conn.ChkpCreateNetwork(name, ipv4NetAddress, subnet,'static', staticIP)
                conn.ChkpPublish()
                conn.LogOutCheckPoint()
                return render(request, self.template_name, {'form': self.form_class(), 'status': 'close'})
        return render(request, self.template_name, {'form': self.form_class(),
                                                    'dummyhide': self.dummyhideNatJS(),
                                                    'dummyStatic': self.dummystaticNatJS(),
                                                    'posturl': 'createnetwork'})