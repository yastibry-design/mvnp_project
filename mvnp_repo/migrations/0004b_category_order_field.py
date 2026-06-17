"""
Migration: add `order` field to Category and expand name max_length to 200
so the long predefined category names fit without truncation.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mvnp_repo", "0004_cloudinary_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AddField(
            model_name="category",
            name="order",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text="Display order in dropdowns (lower number = first).",
            ),
        ),
    ]
