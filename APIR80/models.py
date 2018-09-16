from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class MGMTServer(models.Model):
    MgmtR80Name = models.CharField(max_length=250)
    ServerIP = models.GenericIPAddressField()
    Description = models.CharField(max_length=500)
    SupportedVersion = (('R80', 'R80'),
                        ('R80.10', 'R80.10'),)
    MgmtR80VersionsSupported = models.CharField(max_length=10, choices=SupportedVersion,default='R80.10')
    MGMTR80IsAlive = models.BooleanField(default=True)
    MgmtFingerPrintAPI = models.CharField(max_length=100, default='not defined')

    def __str__(self):
        return 'MGMTName {} Address {}'.format(self.MgmtR80Name, self.ServerIP)

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