# Generated by Django 5.1.4 on 2025-04-09 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_order_promotions'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pidx',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Khalti Transaction ID'),
        ),
    ]
