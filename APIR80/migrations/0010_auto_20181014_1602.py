# Generated by Django 2.1.1 on 2018-10-14 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APIR80', '0009_mgmtserver_lastpublishsession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mgmtserver',
            name='LastPublishSession',
            field=models.IntegerField(),
        ),
    ]