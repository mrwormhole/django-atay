# Generated by Django 3.1.4 on 2020-12-19 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_productimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='model_number',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
