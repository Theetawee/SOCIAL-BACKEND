# Generated by Django 5.1.1 on 2024-09-25 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_imagemedia_delete_media'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagemedia',
            old_name='image',
            new_name='image_url',
        ),
    ]