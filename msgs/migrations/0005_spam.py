# Generated by Django 4.1.5 on 2023-04-16 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("msgs", "0004_alter_message_receiver_alter_message_sender"),
    ]

    operations = [
        migrations.CreateModel(
            name="Spam",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_checked", models.BooleanField(default=False)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="msgs.message"
                    ),
                ),
            ],
        ),
    ]
