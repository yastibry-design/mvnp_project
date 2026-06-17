# MVNP Research Repository — Django Setup Guide
## Mahagnao Volcano Natural Park · Official Research Archive

---

## WHAT THIS IS

A full Python/Django conversion of the original static HTML site.
- **Home** — statistics, featured studies, latest research
- **Repository** — searchable & filterable table of all studies
- **Viewer** — in-browser PDF viewer with metadata
- **About** — mission & governance
- **Contact** — PAMO contact info & research application link
- **Django Admin** — add/edit studies, upload PDFs without touching code

---

## FOLDER STRUCTURE (what you downloaded)

```
mvnp_repo/
│
├── config/                  ← Django project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── mvnp_repo/               ← Main app
│   ├── migrations/
│   ├── templates/
│   │   └── mvnp_repo/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── repository.html
│   │       ├── viewer.html
│   │       ├── about.html
│   │       └── contact.html
│   ├── management/
│   │   └── commands/
│   │       └── seed_studies.py   ← loads the 3 initial studies
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── static/
│   └── assets/
│       ├── DENR Logo.png
│       ├── MVNP Logo.png
│       └── MVNP Research Guidelines-12242025.pdf
│
├── media/
│   └── repository/              ← PDF files live here
│       ├── Francisco et al_2001_Bathymetry.pdf
│       ├── Preciados et al_2020.pdf
│       └── Modina et al_2024.pdf
│
├── manage.py
└── requirements.txt
```

---

## STEP-BY-STEP SETUP

### STEP 1 — Install Python
Make sure Python 3.10 or higher is installed.
Open a terminal/command prompt and type:
```
python --version
```
If it shows Python 3.10+ you are good. If not, download from https://python.org

---

### STEP 2 — Open a terminal inside the project folder
On Windows: right-click the `mvnp_repo` folder → "Open in Terminal" (or open Command Prompt and `cd` into it)
On Mac/Linux: open Terminal and run:
```
cd /path/to/mvnp_repo
```

---

### STEP 3 — Create a virtual environment
```
python -m venv venv
```

---

### STEP 4 — Activate the virtual environment

**Windows (Command Prompt):**
```
venv\Scripts\activate
```

**Windows (PowerShell):**
```
venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```
source venv/bin/activate
```

You will see `(venv)` appear at the start of your prompt. That means it worked.

---

### STEP 5 — Install Django and dependencies
```
pip install -r requirements.txt
```
Wait for it to finish. It installs Django and Pillow (for image handling).

---

### STEP 6 — Create the database
```
python manage.py migrate
```
This creates the `db.sqlite3` file and all the tables needed.

---

### STEP 7 — Load the 3 initial studies + PDFs
```
python manage.py seed_studies
```
This reads the PDFs already in `media/repository/` and saves them to the database.
You should see:
```
  ✅ Created: francisco2001
  ✅ Created: preciados2020
  ✅ Created: modina2024
✔  Seed complete! 3 studies loaded.
```

---

### STEP 8 — Create a superuser (admin account)
```
python manage.py createsuperuser
```
It will ask you for:
- **Username** — type anything, e.g. `admin`
- **Email** — can be blank, just press Enter
- **Password** — type a password (it won't show while typing)
- **Confirm Password** — type it again

---

### STEP 9 — Run the development server
```
python manage.py runserver
```
You will see something like:
```
Starting development server at http://127.0.0.1:8000/
```

---

### STEP 10 — Open the website in your browser

| Page         | URL                                       |
|--------------|-------------------------------------------|
| Home         | http://127.0.0.1:8000/                    |
| Repository   | http://127.0.0.1:8000/repository/         |
| About        | http://127.0.0.1:8000/about/              |
| Contact      | http://127.0.0.1:8000/contact/            |
| Admin Panel  | http://127.0.0.1:8000/admin/              |

---

## HOW TO ADD A NEW STUDY (no coding needed)

1. Go to **http://127.0.0.1:8000/admin/**
2. Log in with the superuser account you created in Step 8
3. Click **Studies** under MVNP_REPO
4. Click **ADD STUDY** (top right)
5. Fill in the fields:
   - **Study id** — short unique code, e.g. `smith2023` *(no spaces, no special chars)*
   - **Title** — full study title
   - **Authors** — author names
   - **Year** — publication year as a number
   - **Category** — pick from the dropdown (or add a new one via the + button)
   - **Study type** — Journal Article / Technical Report / Thesis / Other
   - **Status** — Legacy Study or MVNP-PAMB Approved Publication
   - **Featured** — check this box to show the study on the homepage
   - **Abstract** — short summary paragraph
   - **Pdf file** — click "Choose File" and upload the PDF
6. Scroll down, add keywords using the inline form (word by word)
7. Click **SAVE**

The study will immediately appear in the Repository page.

---

## HOW TO SEARCH THE REPOSITORY

On the **Repository** page (http://127.0.0.1:8000/repository/):
- Type in the **search box** to find by title, author, year, or keyword
- Use the **Type** dropdown to filter by Journal Article, Technical Report, etc.
- Use the **Status** dropdown to filter by approval status
- Use the **Category** dropdown to filter by research discipline
- Click **Clear** to reset all filters

---

## HOW TO VIEW A STUDY / PDF

On the Repository page, click the green **View Study** button in any row.
This opens the **Viewer** page which shows:
- Study title, authors, year, type, category
- The abstract
- Keywords (tags)
- A **Download PDF** button (opens in a new tab)
- An embedded PDF iframe (you can read it directly in the browser)

---

## STOPPING THE SERVER

Press **Ctrl + C** in the terminal where `runserver` is running.

---

## RESTARTING LATER

Every time you want to use the site again:
```
# From inside the mvnp_repo folder:
source venv/bin/activate    # Mac/Linux
# or
venv\Scripts\activate       # Windows

python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

---

## TROUBLESHOOTING

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'django'` | You forgot to activate the venv — run the activate command in Step 4 again |
| `python: command not found` | Use `python3` instead of `python` on some Mac/Linux systems |
| Page shows "No studies found" | Run `python manage.py seed_studies` again |
| PDF shows blank in viewer | The browser may block local file embeds — click "Download PDF" to open it directly |
| Port already in use | Use `python manage.py runserver 8080` to run on a different port, then visit http://127.0.0.1:8080/ |

---

*MVNP Research Repository · Protected Area Management Office · DENR*
