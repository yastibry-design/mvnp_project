import requests as http_requests
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Min, Max
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin
from .models import Study, Category, ResearchApplication
from django.contrib.auth import update_session_auth_hash
from .forms import StudyForm, UserForm, ResearchApplicationForm, ProfileForm, ProfilePasswordChangeForm


# ─── shared stats helper ──────────────────────────────────────────────────────

def _repo_stats():
    qs = Study.objects.all()
    total    = qs.count()
    journals = qs.filter(study_type='Journal Article').count()
    agg      = qs.aggregate(mn=Min('year'), mx=Max('year'))
    span = (agg['mx'] - agg['mn'] + 1) if (agg['mn'] and agg['mx']) else 0
    return {
        'total_studies':    total,
        'journal_articles': journals,
        'research_years':   span,
    }


LOGIN_LOCKOUT_SECONDS = 15 * 60
LOGIN_LOCKOUT_MAX_MISSING_ACCOUNT_ATTEMPTS = 5


def _visitor_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _login_lock_key(request):
    return f'login_lockout:{_visitor_ip(request)}'


def _login_missing_account_attempts_key(request):
    return f'login_missing_account_attempts:{_visitor_ip(request)}'


def _lock_login(request):
    lock_expires_at = timezone.now() + timezone.timedelta(seconds=LOGIN_LOCKOUT_SECONDS)
    cache.set(_login_lock_key(request), lock_expires_at, LOGIN_LOCKOUT_SECONDS)
    cache.delete(_login_missing_account_attempts_key(request))


def _record_missing_account_attempt(request):
    key = _login_missing_account_attempts_key(request)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
    return attempts


def _login_lock_remaining_minutes(request):
    lock_expires_at = cache.get(_login_lock_key(request))
    if not lock_expires_at:
        return None

    remaining_seconds = int((lock_expires_at - timezone.now()).total_seconds())
    if remaining_seconds <= 0:
        cache.delete(_login_lock_key(request))
        return None

    return max(1, (remaining_seconds + 59) // 60)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)
    remaining_minutes = _login_lock_remaining_minutes(request)
    if remaining_minutes:
        login_error = (
            f'Too many login attempts with an account that does not exist. '
            f'Please try again in {remaining_minutes} minute(s).'
        )
        return render(request, 'mvnp_repo/login.html', {
            'form': form,
            'login_locked': True,
            'login_error': login_error,
        })

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if username and not User.objects.filter(username__iexact=username).exists():
            attempts = _record_missing_account_attempt(request)
            if attempts >= LOGIN_LOCKOUT_MAX_MISSING_ACCOUNT_ATTEMPTS:
                _lock_login(request)
                login_error = (
                    'Too many login attempts with accounts that do not exist. '
                    'Please wait 15 minutes before trying again.'
                )
            else:
                remaining_attempts = LOGIN_LOCKOUT_MAX_MISSING_ACCOUNT_ATTEMPTS - attempts
                login_error = (
                    f'That account does not exist. '
                    f'{remaining_attempts} attempt(s) remaining before a 15-minute lock.'
                )
            return render(request, 'mvnp_repo/login.html', {
                'form': form,
                'login_error': login_error,
            })

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.is_staff:
            messages.success(request, f' You have successfully logged in.')
        else:
            messages.success(request, f' You have successfully logged in.')
        return redirect(request.GET.get('next') or 'home')

    return render(request, 'mvnp_repo/login.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'mvnp_repo/signup.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            messages.success(request, f'You have been successfully logged out.')
        else:
            messages.success(request, f'You have been successfully logged out.')
    logout(request)
    return redirect('home')


def _require_staff(request):
    if not request.user.is_staff:
        raise PermissionDenied('Administrator privileges required.')


def user_list(request):
    _require_staff(request)
    q = request.GET.get('q', '').strip()
    users = User.objects.order_by('-date_joined')
    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q)
        )
    return render(request, 'mvnp_repo/user_list.html', {
        'users': users,
        'q': q,
    })


def user_add(request):
    _require_staff(request)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User account created successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Please correct the errors and try again.')
    else:
        form = UserCreationForm()

    return render(request, 'mvnp_repo/user_form.html', {
        'form': form,
        'page_title': 'Create Account',
        'submit_label': 'Create User',
    })


def user_edit(request, user_id):
    _require_staff(request)
    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'User account updated successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Please correct the errors and try again.')
    else:
        form = UserForm(instance=user_obj)

    return render(request, 'mvnp_repo/user_form.html', {
        'form': form,
        'page_title': f'Edit {user_obj.username}',
        'submit_label': 'Save Changes',
        'user_obj': user_obj,
    })


def user_delete(request, user_id):
    _require_staff(request)
    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(request, 'You cannot delete your own account while logged in.')
            return redirect('user_list')
        user_obj.delete()
        messages.success(request, 'User account deleted successfully.')
        return redirect('user_list')

    return render(request, 'mvnp_repo/user_confirm_delete.html', {
        'user_obj': user_obj,
    })


def study_create(request):
    _require_staff(request)

    if request.method == 'POST':
        form = StudyForm(request.POST, request.FILES)
        if form.is_valid():
            study = form.save()
            messages.success(request, 'Research study added successfully.')
            return redirect('viewer', study_id=study.study_id)
        else:
            messages.error(request, 'Please fix the highlighted errors and try again.')
    else:
        form = StudyForm()

    return render(request, 'mvnp_repo/study_form.html', {
        'form': form,
        'page_title': 'Add Research',
        'submit_label': 'Create Study',
    })


def study_update(request, study_id):
    _require_staff(request)

    study = get_object_or_404(Study, study_id=study_id)
    if request.method == 'POST':
        form = StudyForm(request.POST, request.FILES, instance=study)
        if form.is_valid():
            study = form.save()
            messages.success(request, 'Research study updated successfully.')
            return redirect('viewer', study_id=study.study_id)
        else:
            messages.error(request, 'Please fix the highlighted errors and try again.')
    else:
        form = StudyForm(instance=study)

    return render(request, 'mvnp_repo/study_form.html', {
        'form': form,
        'page_title': 'Edit Research',
        'submit_label': 'Save Changes',
        'study': study,
    })


def study_delete(request, study_id):
    _require_staff(request)

    study = get_object_or_404(Study, study_id=study_id)
    if request.method == 'POST':
        study.delete()
        messages.success(request, 'Research study deleted successfully.')
        return redirect('repository')

    return render(request, 'mvnp_repo/study_confirm_delete.html', {
        'study': study,
    })


# ─── PDF Proxy ────────────────────────────────────────────────────────────────

@xframe_options_sameorigin
@login_required(login_url='login')
def pdf_proxy(request, study_id):
    import os
    from django.conf import settings as django_settings

    study = get_object_or_404(Study, study_id=study_id)
    if not study.pdf_file:
        raise Http404('No PDF attached to this study.')

    pdf_bytes = None

    # ── 1. Serve from local media/ (works for all newly uploaded studies) ────
    #
    # When admin uploads a PDF via the Add Research form, Django saves a local
    # copy under MEDIA_ROOT before Cloudinary processes it. We serve that copy
    # directly — it always exists for local development.
    #
    # The stored value is either:
    #   a) A real relative path like "repository/Modina_et_al_2024.pdf"
    #   b) A Cloudinary public ID like "mvnp/repository/bfc7jtwvfesnp5xidtup"
    #      (for older seeded studies that were never uploaded locally via form)

    stored = str(study.pdf_file)
    repo_dir = os.path.join(django_settings.MEDIA_ROOT, 'repository')

    # Build candidate local paths to try in order:
    candidate_paths = [
        # Direct: stored value is already a relative path inside MEDIA_ROOT
        os.path.join(django_settings.MEDIA_ROOT, stored),
        os.path.join(django_settings.MEDIA_ROOT, stored + '.pdf'),
    ]

    if os.path.isdir(repo_dir):
        try:
            year_str = str(study.year)
            # Strategy A: match by first author last name + year
            first_author_last = study.authors.split(',')[0].split()[-1].lower()
            # Strategy B: match by study_id prefix (e.g. "francisco" from "francisco2001")
            #   Strip the trailing year digits to get the name portion of the slug
            slug_name = study_id.rstrip('0123456789').lower()

            for fname in sorted(os.listdir(repo_dir)):
                if not fname.lower().endswith('.pdf'):
                    continue
                fname_lower = fname.lower()
                year_match = year_str in fname_lower
                # Accept if EITHER author-name OR slug-name matches, plus year
                if year_match and (
                    (first_author_last and first_author_last in fname_lower) or
                    (slug_name and slug_name in fname_lower)
                ):
                    candidate_paths.insert(0, os.path.join(repo_dir, fname))
        except Exception:
            pass

    for path in candidate_paths:
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                pdf_bytes = f.read()
            break

    # ── 2. Fall back to Cloudinary (production / deployment path) ────────────
    if pdf_bytes is None:
        cloudinary_url = study.pdf_url
        print(f"DEBUG pdf_proxy: stored={str(study.pdf_file)!r}, cloudinary_url={cloudinary_url!r}")
        if cloudinary_url:
            try:
                r = http_requests.get(cloudinary_url, timeout=30)
                print(f"DEBUG pdf_proxy: HTTP status={r.status_code}")
                if r.status_code == 200:
                    pdf_bytes = r.content
                else:
                    # Try unsigned URL as fallback
                    import cloudinary
                    resource = study.pdf_file
                    unsigned_url = cloudinary.CloudinaryResource(
                        resource.public_id,
                        resource_type=resource.resource_type or 'raw',
                    ).build_url(secure=True)
                    print(f"DEBUG pdf_proxy: trying unsigned_url={unsigned_url!r}")
                    r2 = http_requests.get(unsigned_url, timeout=30)
                    print(f"DEBUG pdf_proxy: unsigned HTTP status={r2.status_code}")
                    if r2.status_code == 200:
                        pdf_bytes = r2.content
            except Exception as e:
                print(f"DEBUG pdf_proxy: exception={e}")
                pass

    if pdf_bytes is None:
        raise Http404('PDF could not be retrieved. File not found locally or on Cloudinary.')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{study.study_id}.pdf"'
    return response


# ─── Home ─────────────────────────────────────────────────────────────────────

def home(request):
    featured = (Study.objects.filter(featured=True)
                .select_related('category')
                .prefetch_related('keywords')
                .order_by('-year'))

    latest = (Study.objects.all()
              .select_related('category')
              .order_by('-year')[:5])

    highlights = {
        'earliest': Study.objects.aggregate(mn=Min('year'))['mn'] or '—',
        'latest':   Study.objects.aggregate(mx=Max('year'))['mx'] or '—',
        'cat_names': list(
            Category.objects.filter(studies__isnull=False)
            .distinct()
            .values_list('name', flat=True)
        ),
    }

    ctx = {
        'featured':   featured,
        'latest':     latest,
        'highlights': highlights,
        **_repo_stats(),
    }
    return render(request, 'mvnp_repo/home.html', ctx)


# ─── Repository ───────────────────────────────────────────────────────────────

@login_required(login_url='login')
def repository(request):
    studies = (Study.objects.all()
               .select_related('category')
               .prefetch_related('keywords')
               .order_by('-year', 'title'))

    q      = request.GET.get('q', '').strip()
    ftype  = request.GET.get('type', '').strip()
    fstat  = request.GET.get('status', '').strip()
    fcat   = request.GET.get('category', '').strip()

    if q:
        studies = studies.filter(
            Q(title__icontains=q) |
            Q(authors__icontains=q) |
            Q(year__icontains=q) |
            Q(abstract__icontains=q) |
            Q(keywords__word__icontains=q)
        ).distinct()
    if ftype:
        studies = studies.filter(study_type=ftype)
    if fstat:
        studies = studies.filter(status=fstat)
    if fcat:
        studies = studies.filter(category__name=fcat)

    categories = Category.objects.all()

    ctx = {
        'studies':    studies,
        'categories': categories,
        'type_choices':   Study.TYPE_CHOICES,
        'status_choices': Study.STATUS_CHOICES,
        'q':     q,
        'ftype': ftype,
        'fstat': fstat,
        'fcat':  fcat,
        'total': studies.count(),
        **_repo_stats(),
    }
    return render(request, 'mvnp_repo/repository.html', ctx)


# ─── Viewer ───────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def viewer(request, study_id):
    study = get_object_or_404(
        Study.objects.select_related('category').prefetch_related('keywords'),
        study_id=study_id
    )
    return render(request, 'mvnp_repo/viewer.html', {'study': study})


# ─── About ────────────────────────────────────────────────────────────────────

def about(request):
    return render(request, 'mvnp_repo/about.html', _repo_stats())


# ─── Research Application ─────────────────────────────────────────────────────

def research_application(request):
    if request.user.is_authenticated and request.user.is_staff:
        messages.info(request, 'Admin accounts cannot submit research applications. View submitted applications instead.')
        return redirect('application_list')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            from django.urls import reverse
            return redirect(reverse('login') + f'?next={request.path}')
        form = ResearchApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            application.notify_mvnp_on_submission()
            messages.success(request, 'Your research application has been submitted. MVNP staff will review it shortly.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the form errors and try again.')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'applicant_name': request.user.get_full_name() or request.user.username,
                'applicant_email': request.user.email,
            }
        form = ResearchApplicationForm(initial=initial)

    return render(request, 'mvnp_repo/research_application.html', {
        'form': form,
    })


@login_required(login_url='login')
def application_list(request):
    _require_staff(request)
    applications = (ResearchApplication.objects
                    .select_related('user', 'reviewer')
                    .order_by('-submitted_at'))

    pending  = applications.filter(status='Pending')
    approved = applications.filter(status='Approved')
    declined = applications.filter(status='Declined')

    return render(request, 'mvnp_repo/application_list.html', {
        'applications': applications,
        'pending':      pending,
        'approved':     approved,
        'declined':     declined,
        'pending_count':  pending.count(),
        'approved_count': approved.count(),
        'declined_count': declined.count(),
    })


@login_required(login_url='login')
def application_review(request, application_id, action):
    _require_staff(request)
    application = get_object_or_404(ResearchApplication, pk=application_id)

    if application.status != 'Pending':
        messages.info(request, 'This application has already been reviewed.')
        return redirect('application_list')

    if request.method == 'POST':
        if action == 'approve':
            application.status = 'Approved'
        elif action == 'reject':
            application.status = 'Declined'
        else:
            messages.error(request, 'Invalid review action.')
            return redirect('application_list')

        application.reviewer = request.user
        application.reviewed_at = timezone.now()
        application.save()
        application.send_status_notification()
        messages.success(request, f'Application has been {application.status.lower()} successfully.')

    return redirect('application_list')


@login_required(login_url='login')
def my_applications(request):
    applications = (ResearchApplication.objects
                    .filter(user=request.user)
                    .order_by('-submitted_at'))

    pending_count  = applications.filter(status='Pending').count()
    approved_count = applications.filter(status='Approved').count()
    declined_count = applications.filter(status='Declined').count()

    return render(request, 'mvnp_repo/my_applications.html', {
        'applications':  applications,
        'pending_count':  pending_count,
        'approved_count': approved_count,
        'declined_count': declined_count,
    })


def contact(request):
    return render(request, 'mvnp_repo/contact.html')

# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def profile_update(request):
    """Update first name, last name, and email for the logged-in user."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required(login_url='login')
def profile_password_change(request):
    """Change password for the logged-in user."""
    if request.method == 'POST':
        form = ProfilePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            messages.success(request, 'Your password has been changed successfully.')
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
    return redirect(request.META.get('HTTP_REFERER', 'home'))