# Generated by Django 3.2.19 on 2023-07-03 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('magento_integration_app', '0003_auto_20230628_2220'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.session'),
        ),
    ]
