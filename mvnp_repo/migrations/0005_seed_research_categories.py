"""
Data migration: seed the three predefined research categories.

Categories (in display order):
  1. Non-invasive (e.g., biodiversity surveys, visual observations)
  2. Sampling-based / minimal collection
  3. Commercial / high-impact
"""
from django.db import migrations


CATEGORIES = [
    (1, "Non-invasive (e.g., biodiversity surveys, visual observations)"),
    (2, "Sampling-based / minimal collection"),
    (3, "Commercial / high-impact"),
]

NAMES_ONLY = [name for _, name in CATEGORIES]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("mvnp_repo", "Category")
    for order, name in CATEGORIES:
        obj, _ = Category.objects.get_or_create(name=name)
        if obj.order != order:
            obj.order = order
            obj.save()


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("mvnp_repo", "Category")
    Category.objects.filter(name__in=NAMES_ONLY).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("mvnp_repo", "0004b_category_order_field"),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=unseed_categories),
    ]
