# Generated by Django 5.0.1 on 2024-03-19 07:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_contentimage_comment_alter_contentimage_post"),
        ("sockets", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notification",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="notification",
            name="post",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.post",
            ),
        ),
    ]
