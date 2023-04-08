# Generated by Django 4.2 on 2023-04-06 07:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("flavors", "0003_alter_flavor_img"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
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
                ("is_anonymous", models.BooleanField(blank=True, default=False)),
                ("content", models.CharField(max_length=255)),
                ("is_success", models.BooleanField(blank=True, default=False)),
                ("is_read", models.BooleanField(blank=True, default=False)),
                ("sender_deleted", models.BooleanField(blank=True, default=False)),
                ("receiver_deleted", models.BooleanField(blank=True, default=False)),
                ("is_spam", models.BooleanField(blank=True, default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "flavor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="flavors.flavor"
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        default="사라진쿠키",
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="receiver",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        default="사라진쿠키",
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="sender",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
