# Generated by Django 4.1.5 on 2023-04-16 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
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
                (
                    "title",
                    models.CharField(
                        choices=[("E", "오류"), ("U", "불편사항"), ("R", "건의사항")],
                        max_length=10,
                    ),
                ),
                ("content", models.CharField(max_length=255)),
                ("is_checked", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        default=11,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]