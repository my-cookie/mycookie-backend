# Generated by Django 4.2 on 2023-04-06 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("msgs", "0002_alter_message_is_anonymous"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="is_anonymous",
            field=models.BooleanField(),
        ),
    ]
