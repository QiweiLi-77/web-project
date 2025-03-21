# Generated by Django 4.1.7 on 2025-03-20 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('commodity', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shopper', '0002_alter_orderinfos_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectInfos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation Time')),
                ('commodityInfos_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='commodity.commodityinfos', verbose_name='Product')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
                'unique_together': {('user_id', 'commodityInfos_id')},
            },
        ),
    ]
