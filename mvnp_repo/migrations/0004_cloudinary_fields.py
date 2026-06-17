"""
Migration: swap FileField -> CloudinaryField on Study.pdf_file
and ResearchApplication.supporting_documents.

Existing rows that stored a local path keep their string value in the
database. Cloudinary stores public_ids as strings the same way Django
stores file paths, so no data is lost.
"""
from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ('mvnp_repo', '0003_researchapplication_reviewed_at_and_more'),
    ]

    operations = [
        # ── Study.pdf_file ────────────────────────────────────────────────────
        migrations.AlterField(
            model_name='study',
            name='pdf_file',
            field=cloudinary.models.CloudinaryField(
                'pdf_file',
                resource_type='raw',
                folder='mvnp/repository',
                null=True,
                blank=True,
            ),
        ),
        # ── ResearchApplication.supporting_documents ──────────────────────────
        migrations.AlterField(
            model_name='researchapplication',
            name='supporting_documents',
            field=cloudinary.models.CloudinaryField(
                'supporting_documents',
                resource_type='raw',
                folder='mvnp/applications',
                null=True,
                blank=True,
            ),
        ),
    ]
