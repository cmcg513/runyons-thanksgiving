# Generated by Django 2.1.2 on 2018-10-21 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_registrar_registration_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrar',
            name='phone',
            field=models.CharField(default=5555555555, max_length=10),
            preserve_default=False,
        ),
    ]
