from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import MaxValueValidator
from chkp import settings

# Create your models here.
class MGMTServer(models.Model):
    ApiSupportedVersions = (('1_1', '1_1'),)
    MgmtR80Name = models.CharField(max_length=250)
    ServerIP = models.GenericIPAddressField()
    Description = models.TextField(max_length=500)
    SupportedVersion = (('R80', 'R80'),
                        ('R8010', 'R80.10'),)
    MgmtR80VersionsSupported = models.CharField(max_length=10, choices=SupportedVersion,default='R80.10')
    MgmtR80ApiVersion = models.CharField(max_length=4, choices = ApiSupportedVersions, default='1_1')
    MGMTR80IsAlive = models.BooleanField(default=True)
    MgmtFingerPrintAPI = models.CharField(max_length=100, default='not defined')
    MgmtPort = models.PositiveIntegerField(validators=[MaxValueValidator(65525)], default=443)
    LastPublishSession = models.IntegerField(default=1)

    def __str__(self):
        return 'MGMTName {} Address {}'.format(self.MgmtR80Name, self.ServerIP)

class MGMTServerObjects(models.Model):
    MGMTServerObjectsID = models.ForeignKey(MGMTServer, on_delete=models.CASCADE)
    MGMTServerFilePathTCPPorts = models.CharField(max_length=250, default='{}/APIR80/tmp/chkpports.txt'.format(settings.BASE_DIR))
    MGMTServerFilePathUDPPorts = models.CharField(max_length=250, default='{}/APIR80/tmp/chkpudpports.txt'.format(settings.BASE_DIR))
    MGMTServerFilePathNetObjects = models.CharField(max_length=250,default='{}/APIR80/tmp/chkpobjects.txt'.format(settings.BASE_DIR))
    MGMTServerFilePathNetworksObjects = models.CharField(max_length=250, default='{}/APIR80/tmp/chkpobjectsnetworks.txt'.format(settings.BASE_DIR))

# class MGMTServerObjectsNetworks(models.Model):
#     MGMTServerObjectsNetworksID = models.ForeignKey(MGMTServer, on_delete=models.CASCADE)
#     MGMTServerFilePathNetObjects = models.CharField(max_length=250, default='{}/APIR80/tmp/chkpobjects.txt'.format(settings.BASE_DIR))

class R80Users(models.Model):
    UsersID = models.ForeignKey(MGMTServer, on_delete=models.CASCADE)
    R80User = models.CharField(max_length=30)
    R80Password = models.CharField(max_length=50)

    def __str__(self):
        return self.R80User

class AnsibleGeneralDeploy(models.Model):
    AnsibleResourceGroup = models.CharField(max_length = 20)
    AnsibleTMLocation = models.CharField(max_length = 10)
    AnsibleCredentials = models.OneToOneField(R80Users, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return 'AnsibleGeneralDeploy ' + AnsibleResourceGroup


class ZeroTouchLoginModel(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)