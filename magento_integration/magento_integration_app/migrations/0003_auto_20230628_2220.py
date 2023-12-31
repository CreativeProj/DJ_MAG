# Generated by Django 3.2.19 on 2023-06-28 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('magento_integration_app', '0002_auto_20230628_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('magento_sku', models.CharField(max_length=100, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('address', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=20)),
                ('is_subscribed', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='magento_integration_app.customer'),
        ),
    ]
