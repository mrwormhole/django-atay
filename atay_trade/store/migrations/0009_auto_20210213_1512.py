# Generated by Django 3.1.6 on 2021-02-13 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_auto_20210212_0214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.customer'),
        ),
    ]