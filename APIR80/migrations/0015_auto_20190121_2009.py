# Generated by Django 2.1.1 on 2019-01-21 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APIR80', '0014_auto_20190111_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mgmtserverobjects',
            name='MGMTServerFilePathNetObjects',
            field=models.CharField(default='/home/carlos/django-chkp/APIR80/tmp/chkpobjects.txt', max_length=250),
        ),
        migrations.AlterField(
            model_name='mgmtserverobjects',
            name='MGMTServerFilePathNetworksObjects',
            field=models.CharField(default='/home/carlos/django-chkp/APIR80/tmp/chkpobjectsnetworks.txt', max_length=250),
        ),
        migrations.AlterField(
            model_name='mgmtserverobjects',
            name='MGMTServerFilePathTCPPorts',
            field=models.CharField(default='/home/carlos/django-chkp/APIR80/tmp/chkpports.txt', max_length=250),
        ),
        migrations.AlterField(
            model_name='mgmtserverobjects',
            name='MGMTServerFilePathUDPPorts',
            field=models.CharField(default='/home/carlos/django-chkp/APIR80/tmp/chkpudpports.txt', max_length=250),
        ),
    ]
