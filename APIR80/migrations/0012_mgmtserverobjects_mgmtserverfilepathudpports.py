# Generated by Django 2.1.1 on 2018-10-21 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APIR80', '0011_auto_20181014_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='mgmtserverobjects',
            name='MGMTServerFilePathUDPPorts',
            field=models.CharField(default='/home/carlos/django-chkp/APIR80/tmp/chkpudpports.txt', max_length=250),
        ),
    ]