# Generated by Django 4.1.5 on 2023-04-10 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bookmarks", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookmark",
            name="target",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bookmark_target",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
