# Generated by Django 2.2.7 on 2020-01-12 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TwiSenApp', '0003_auto_20200112_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='since',
            field=models.DateField(null=True),
        ),
    ]
