# Generated by Django 4.1.5 on 2023-04-18 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_temporalnickname_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="BannedUser",
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
                ("username", models.CharField(max_length=20, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]