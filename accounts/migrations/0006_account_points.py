# Generated by Django 5.1.1 on 2024-10-21 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='points',
            field=models.IntegerField(default=0),
        ),
    ]
