# Generated by Django 5.1.1 on 2024-10-05 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_account_verified_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='tagline',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]