# Generated by Django 4.1.5 on 2023-04-18 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_banneduser"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={},
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["nickname", "uuid"], name="users_user_nicknam_f432f0_idx"
            ),
        ),
    ]
