from background_task import background
import json, http.client, httplib2
import os, ssl
from django.http import HttpResponse
from django.http import Http404

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

    def __ChkpValidateSID(self):
        try:
            sid = self.Headers['X-chkp-sid']
        except KeyError:
            raise Http404('BackEnd Error lets try first with a Login')

    def __ChkpValidConnection(self, Path, body, method = 'POST'):
        try:
            self.connection.request(method, Path, headers=self.Headers, body=body)
        except Exception:
            raise Http404("Error sending data to backend")

    def __ChkpCheckHTTPReturnCode(self, conn):
        print("Connection Status {}".format(conn.status))
        if str(conn.status) in self.APIErrors:
            raise Http404('API Error Code {}'.format(conn.status))

    def ChkpLogin(self, user, password):
        """Agregar mas validadores
            SID
            connection
            Validar el status code con
                response = self.connection.getresponse()
                 print(response.status)
            No solo el tamaño del SID
        """
        PathAppend = '/web_api/login'
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
        self.__ChkpCheckHTTPReturnCode(conn)
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
        PathAppend = '/web_api/publish'
        data = { }
        jdata = json.dumps(data)
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        #print(response)

    def LogOutCheckPoint(self):
        print('Logout function')
        PathAppend = '/web_api/logout'
        data = { }
        jdata = json.dumps(data)
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        print(response)
        if response['message'] != "OK":
            raise Http404("Invalid LogOut")
        return True

    def ChkpAddAccessLayer(self, LayerNane):
        print('Access layer')
        PathAppend = '/web_api/add-access-layer'
        data = {
            'name': LayerNane,
            'add-default-rule': True,
            'firewall': True
        }
        jdata = json.JSONEncoder().encode(data)
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        #print("aaaaaaaa {}".format(response))
        #{'code': 'generic_err_invalid_parameter_name', 'message': 'Unrecognized parameter [implicit-cleanup-action]'}

    def ChkpSetLayerDefaultRuleToAccept(self, rulename, layer, action='Accept'):
        print('default rule to accept')
        PathAppend = '/web_api/set-access-rule'
        data = {
            'name': rulename,
            'layer': layer,
            'action': action
        }
        jdata = json.JSONEncoder().encode(data)
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        print("bbbbb {}".format(conn.read().decode()))

    def ChkpAddAccesRule(self, layer, name, source,
                         destination, service, action, track):
        PathAppend = "/web_api/add-access-rule"
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
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response


    def ChkpShowServicesTCP(self, offset=0, limit=217):
        PathAppend = '/web_api/show-services-tcp'
        data = {
            'limit': limit,
            'offset': offset,
            'details-level':  "standard"
        }
        jdata = json.JSONEncoder().encode(data)
        self.__ChkpValidateSID()
        # for i in range(retries):
        #     try:
        #         self.connection.request('POST', PathAppend, headers=self.Headers, body=jdata)
        #     except http.client.RemoteDisconnected:
        #         if i < retries:
        #             continue
        #         else:
        #             raise Http404('Max Retries for Show Services')
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpShowHosts(self, offset=0, limit=217):
        PathAppend = '/web_api/show-hosts'
        data = {
            'limit': limit,
            'offset': offset,
            'details-level': "standard"
        }
        jdata = json.JSONEncoder().encode(data)
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response = json.loads(conn.read().decode())
        return response

    def ChkpShowLastPublishedSession(self):
        PathAppend = "/web_api/show-last-published-session"
        data = { }
        jdata = json.JSONEncoder().encode(data)
        self.__ChkpValidateSID()
        self.__ChkpValidConnection(PathAppend, jdata)
        conn = self.connection.getresponse()
        self.__ChkpCheckHTTPReturnCode(conn)
        response= json.loads(conn.read().decode())
        return response

class CheckPointEConnection(CheckPointAPI):
    def __init__(self, user, password, IP):
        self.user = user
        self.password = password
        self.IP = IP
        super().__init__(IP)
        self.ConnectionData= super().ChkpLogin()



@background
def counttomil():
    for i in range(1000):
        print("Tarea programanada {}".format(i))

