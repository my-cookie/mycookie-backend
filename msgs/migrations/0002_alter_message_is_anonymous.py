# Generated by Django 4.2 on 2023-04-06 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("msgs", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="is_anonymous",
            field=models.BooleanField(default=True),
        ),
    ]
