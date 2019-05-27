from background_task import background
import json, http.client
import os, ssl
from django.http import Http404
import importlib

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

""""
Todo cambiar el codigo

response = json.loads(self.connection.getresponse().read().decode())

Por algo en donde se pueda ir por el status, se puede poner esto como funcion
"""
class CheckPointAPI():
    ChkpPort = 443
    ChkpIP = None
    URI1  = 'web_api'

    def __init__(self, ChkpIP, ChkpPort):
        self.ChkpIP=ChkpIP
        self.ChkpPort=ChkpPort
        self.LoginRead = False
        self.Logout = False
        self.KeepAlive = 10
        self.MaxKeepAliveSeconds = 60
        self.Headers = {'Content-Type':'application/json'}
        self.ChkpURL = '{}:{}'.format(self.ChkpIP, self.ChkpPort)
        self.APIErrors = ['400', '401', '404', '500']

    def __str__(self):
        return("CheckPoint API Connects to: {} and port {} ".format(self.ChkpIP, self.ChkpPort))

    def SetKeepAlive(self, KeepAlive):
        assert KeepAlive >= 0, "KeepAlive Must be an Integer Between 0 and {}".format(self.MaxKeepAliveSeconds)
        assert KeepAlive <= self.MaxKeepAliveSeconds, "KeepAlive Must be an Integer Between 0 and {}".format(self.MaxKeepAliveSeconds)
        self.KeepAlive = KeepAlive

    def ChkpValidateSID(self):
        try:
            sid = self.Headers['X-chkp-sid']
        except KeyError:
            raise Http404('BackEnd Error lets try first with a Login')

    def ChkpValidConnection(self, Path, body, method ='POST'):
        try:
            self.connection.request(method, Path, headers=self.Headers, body=body)
        except Exception:
            raise Http404("Error sending data to backend")

    def ChkpCheckHTTPReturnCode(self, conn):
        print("Connection Status {}".format(conn.status))
        if str(conn.status) in self.APIErrors:
            raise Http404('API Error Code {}'.format(conn.status))



class apiv1_1(CheckPointAPI):
    apiVersion = 'v1.1'

    def ChkpLogin(self, user, password):
        """Agregar mas validadores
            SID
            connection
            Validar el status code con
                response = self.connection.getresponse()
                 print(response.status)
            No solo el tamaño del SID
        """
        c = 'login'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion)>0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'user': user,
            'password': password
        }
        jdata=json.dumps(data)
        #agregar manejo de excepciones como timeout
        self.connection = http.client.HTTPSConnection(self.ChkpURL)
        try:
            self.connection.request("POST", PathAppend, headers=self.Headers, body=jdata)
        except Exception:
            raise Http404("Error sending data to backend")
        #self.__ChkpCheckHTTPReturnCode()
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        #response = json.loads(self.connection.getresponse().read().decode())
        response = json.loads(conn.read().decode())
        print(response)
        if len(response['sid']) <= 0:
            raise Http404("sid data invalid")
        else:
            self.Headers.update({'X-chkp-sid': str(response['sid'])})
        return response['sid']

    def ChkpPublish(self):
        print('publish function')
        c='publish'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion)>0 else '/{}/{}'.format(self.URI1,c)
        data = { }
        jdata = json.dumps(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        #print(response)

    def LogOutCheckPoint(self):
        print('Logout function')
        c='logout'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = { }
        jdata = json.dumps(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        print(response)
        if response['message'] != "OK":
            raise Http404("Invalid LogOut")
        return True

    def ChkpAddAccessLayer(self, LayerNane):
        print('Access layer')
        c='add-access-layer'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'name': LayerNane,
            'add-default-rule': True,
            'firewall': True
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        #print("aaaaaaaa {}".format(response))
        #{'code': 'generic_err_invalid_parameter_name', 'message': 'Unrecognized parameter [implicit-cleanup-action]'}

    def ChkpSetLayerDefaultRuleToAccept(self, rulename, layer, action='Accept'):
        print('default rule to accept')
        c='set-access-rule'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'name': rulename,
            'layer': layer,
            'action': action
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        print("bbbbb {}".format(conn.read().decode()))

    def ChkpAddAccesRule(self, layer, name, source,
                         destination, service, action, track):
        c='add-access-rule'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'layer': layer,
            'position': 'top',
            'name': name,
            'source': source,
            'destination': destination,
            'service': service,
            'action': action,
            'track': {'type': track}
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response


    def ChkpShowServicesTCP(self, offset=0, limit=217):
        c='show-services-tcp'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'limit': limit,
            'offset': offset,
            'details-level':  "standard"
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        # for i in range(retries):
        #     try:
        #         self.connection.request('POST', PathAppend, headers=self.Headers, body=jdata)
        #     except http.client.RemoteDisconnected:
        #         if i < retries:
        #             continue
        #         else:
        #             raise Http404('Max Retries for Show Services')
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpShowNetworks(self, offset=0, limit=217):
        c='show-networks'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'limit': limit,
            'offset': offset,
            'details-level':  "standard"
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpShowFullNetworks(self):
        data = self.ChkpShowNetworks()
        total = data['total']
        if total == 0:
            return data
        else:
            data = self.ChkpShowNetworks(0,total)
            return data

    def ChkpShowFullServicesTCP(self):
        data = self.ChkpShowServicesTCP()
        total = data['total']
        if total == 0:
            return data
        else:
            data = self.ChkpShowServicesTCP(0,total)
            return data

    def ChkpShowServicesUDP(self, offset=0, limit=94):
        c='show-services-udp'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'limit': limit,
            'offset': offset,
            'details-level':  "standard"
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        # for i in range(retries):
        #     try:
        #         self.connection.request('POST', PathAppend, headers=self.Headers, body=jdata)
        #     except http.client.RemoteDisconnected:
        #         if i < retries:
        #             continue
        #         else:
        #             raise Http404('Max Retries for Show Services')
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpShowFullServicesUDP(self):
        data = self.ChkpShowServicesUDP()
        total = data['total']
        if total == 0:
            return data
        else:
            data = self.ChkpShowServicesUDP(0,total)
            return data

    def ChkpShowHosts(self, offset=0, limit=217):
        c='show-hosts'
        PathAppend = '/{}/{}/{}'.format(self.URI1,self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
            'limit': limit,
            'offset': offset,
            'details-level': "standard"
        }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpShowFullHosts(self):
        data = self.ChkpShowHosts()
        total = data['total']
        if total == 0:
            return data
        else:
            data = self.ChkpShowHosts(0,total)
            return data

    def ChkpShowLastPublishedSession(self):
        c='show-last-published-session'
        PathAppend = '/{}/{}/{}'.format(self.URI1, self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = { }
        jdata = json.JSONEncoder().encode(data)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response= json.loads(conn.read().decode())
        return response

    def ChkpCreateHost(self, name, ipv4address, natmethod='no', natparameters='gateway'):
        c='add-host'
        PathAppend = '/{}/{}/{}'.format(self.URI1, self.apiVersion, c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
             'name': name,
             'ip-address': ipv4address
        }
        print("Natmethod {}".format(natmethod))
        if natmethod == 'hide':
            if natparameters == 'gateway':
                data.update({'nat-settings': {'auto-rule': True,
                                          'method': 'hide',
                                          'hide-behind': natparameters}})
            else:
                data.update({'nat-settings': {'auto-rule': True,
                                          'method': 'hide', 'ipv4-address': natparameters,
                                          'hide-behind': 'ip-address'}})
        elif natmethod =='static':
            data.update({'nat-settings': {'auto-rule': True,
                                         'ipv4-address': natparameters, 'method': 'static'}})
        # {'no': lambda: data,
        #     'hide': lambda: data.update({'nat-settings': {'auto-rule': True,
        #                                       'ipv4-address': ipv4address, 'method': 'hide',
        #                                       'hide-behind': hidebehind}}),
        #     'static': lambda: data.update({'auto-rule': True,
        #                                         'ipv4-address': ipv4address, 'method': 'static'})
        # }.get(natmethod, lambda: None)
        jdata = json.JSONEncoder().encode(data)
        print(jdata)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpCreateNetwork(self, name, ipv4address, mask ,natmethod='no', natparameters='gateway'):
        c='add-network'
        PathAppend = '/{}/{}/{}'.format(self.URI1, self.apiVersion,c) if len(self.apiVersion) > 0 else '/{}/{}'.format(self.URI1,c)
        data = {
             'name': name,
             'subnet': ipv4address,
             'mask-length': mask
        }
        print("Natmethod {}".format(natmethod))
        if natmethod == 'hide':
            if natparameters == 'gateway':
                data.update({'nat-settings': {'auto-rule': True,
                                          'method': 'hide',
                                          'hide-behind': natparameters}})
            else:
                data.update({'nat-settings': {'auto-rule': True,
                                          'method': 'hide', 'ipv4-address': natparameters,
                                          'hide-behind': 'ip-address'}})
        elif natmethod =='static':
            data.update({'nat-settings': {'auto-rule': True,
                                         'ipv4-address': natparameters, 'method': 'static'}})
        # {'no': lambda: data,
        #     'hide': lambda: data.update({'nat-settings': {'auto-rule': True,
        #                                       'ipv4-address': ipv4address, 'method': 'hide',
        #                                       'hide-behind': hidebehind}}),
        #     'static': lambda: data.update({'auto-rule': True,
        #                                         'ipv4-address': ipv4address, 'method': 'static'})
        # }.get(natmethod, lambda: None)
        jdata = json.JSONEncoder().encode(data)
        print(jdata)
        self.ChkpValidateSID()
        self.ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

class apiv1_2(apiv1_1):
    def HolaMundoR8020(self):
        print('HolaMundo 8020')

def CheckPointFactory_Connection(MgmtVersion):
    GeneralName = 'apiv' + MgmtVersion
    #print(os.path.basename(__file__))
    NewClass = getattr(importlib.import_module('APIR80.tasks'), GeneralName)
    return NewClass


# class CheckPointEConnection(CheckPointAPI):
#     def __init__(self, user, password, IP):
#         self.user = user
#         self.password = password
#         self.IP = IP
#         super().__init__(IP)
#         self.ConnectionData= super().ChkpLogin()



@background
def counttomil():
    for i in range(1000):
        print("Tarea programanada {}".format(i))

