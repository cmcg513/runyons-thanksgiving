# Generated by Django 2.1.2 on 2018-10-21 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrar',
            name='registration_count',
            field=models.IntegerField(default=0),
        ),
    ]
