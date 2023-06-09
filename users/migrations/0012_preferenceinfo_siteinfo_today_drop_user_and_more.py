# Generated by Django 4.1.5 on 2023-04-26 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0011_siteinfo_created_at_siteinfo_updated_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="PreferenceInfo",
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
                ("flavor", models.CharField(max_length=255)),
                ("flavor_num", models.CharField(max_length=255)),
                ("age", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="siteinfo",
            name="today_drop_user",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="siteinfo",
            name="today_message",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="siteinfo",
            name="today_register_user",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="siteinfo",
            name="today_visit_user",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
