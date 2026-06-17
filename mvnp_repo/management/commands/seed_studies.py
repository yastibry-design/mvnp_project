from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path


DATA = [
    {
        "study_id":   "francisco2001",
        "title":      "Bathymetry and Hydrobiology of Lake Mahagnao",
        "authors":    "Francisco RA, Pundavela MR, Granali JM, Tumabiene LA, Alpino JP and Elmido VV",
        "year":       2001,
        "category":   "Limnology",
        "study_type": "Journal Article",
        "status":     "Legacy Study (Pre-Guidelines)",
        "featured":   True,
        "keywords":   ["Lake", "Bathymetry", "Hydrobiology"],
        "abstract":   (
            "Bathymetric and hydrobiological assessment of Lake Mahagnao including depth "
            "distribution, water quality characteristics and phytoplankton composition."
        ),
        "pdf_filename": "Francisco et al_2001_Bathymetry.pdf",
    },
    {
        "study_id":   "preciados2020",
        "title":      "Economic Valuation of Protected Area Ecosystem Services: The Case of Mahagnao Volcano Natural Park",
        "authors":    "Preciados L., Soria R.J., Polenio F.",
        "year":       2020,
        "category":   "Socioeconomics",
        "study_type": "Journal Article",
        "status":     "MVNP-PAMB Approved Publication",
        "featured":   True,
        "keywords":   ["Economics", "Protected Area", "Ecosystem Services"],
        "abstract":   (
            "Assessment of the economic value of ecosystem services provided by "
            "Mahagnao Volcano Natural Park."
        ),
        "pdf_filename": "Preciados et al_2020.pdf",
    },
    {
        "study_id":   "modina2024",
        "title":      "First Ecological Notes on the Waray Dwarf Burrowing Snake (Levitonius mirus)",
        "authors":    "Modina R.M.R., Cuta C.B.T., Memoracion K.R.C.",
        "year":       2024,
        "category":   "Herpetology",
        "study_type": "Journal Article",
        "status":     "MVNP-PAMB Approved Publication",
        "featured":   True,
        "keywords":   ["Herpetology", "Snake", "Levitonius mirus"],
        "abstract":   (
            "First ecological observations and habitat notes for the Waray Dwarf Burrowing Snake "
            "from Lake Mahagnao."
        ),
        "pdf_filename": "Modina et al_2024.pdf",
    },
]

# Where the PDFs live (relative to manage.py)
PDF_DIR = Path(__file__).resolve().parents[4] / 'media' / 'repository'


class Command(BaseCommand):
    help = 'Seed the database with the three initial MVNP studies'

    def handle(self, *args, **options):
        from mvnp_repo.models import Study, Category, Keyword

        for item in DATA:
            cat, _ = Category.objects.get_or_create(name=item['category'])

            study, created = Study.objects.get_or_create(
                study_id=item['study_id'],
                defaults={
                    'title':      item['title'],
                    'authors':    item['authors'],
                    'year':       item['year'],
                    'category':   cat,
                    'study_type': item['study_type'],
                    'status':     item['status'],
                    'featured':   item['featured'],
                    'abstract':   item['abstract'],
                }
            )

            # Attach PDF file if it exists on disk and not yet attached
            if created or not study.pdf_file:
                pdf_path = PDF_DIR / item['pdf_filename']
                if pdf_path.exists():
                    with open(pdf_path, 'rb') as fh:
                        study.pdf_file.save(item['pdf_filename'], File(fh), save=True)
                    self.stdout.write(f'  📎 Attached {item["pdf_filename"]}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ PDF not found: {pdf_path}')
                    )

            # Add keywords
            for word in item['keywords']:
                Keyword.objects.get_or_create(study=study, word=word)

            verb = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {"✅" if created else "⏭ "} {verb}: {study.study_id}')

        self.stdout.write(self.style.SUCCESS('\n✔  Seed complete! 3 studies loaded.\n'))
