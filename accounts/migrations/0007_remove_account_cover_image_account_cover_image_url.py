# Generated by Django 5.1 on 2024-09-04 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_account_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='cover_image',
        ),
        migrations.AddField(
            model_name='account',
            name='cover_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]