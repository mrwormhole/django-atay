# Generated by Django 3.1.5 on 2021-01-31 13:32

from django.db import migrations, models
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_auto_20210102_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=store.models.upload_to),
        ),
    ]
