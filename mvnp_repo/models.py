from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name  = models.CharField(max_length=200, unique=True)
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Display order in dropdowns (lower number = first).',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']


class Study(models.Model):
    TYPE_CHOICES = [
        ('Journal Article',  'Journal Article'),
        ('Technical Report', 'Technical Report'),
        ('Undergraduate Thesis', 'Undergraduate Thesis'),
        ('Graduate Thesis', 'Graduate Thesis'),
        ('Post-Graduate Thesis', 'Post-Graduate Thesis'),
        ('Other',            'Other'),
    ]
    STATUS_CHOICES = [
        ('Legacy Study (Pre-Guidelines)',    'Legacy Study (Pre-Guidelines)'),
        ('MVNP-PAMB Approved Publication',   'MVNP-PAMB Approved Publication'),
    ]

    study_id   = models.SlugField(max_length=100, unique=True,
                                  help_text='Unique slug, e.g. francisco2001')
    title      = models.CharField(max_length=500)
    authors    = models.CharField(max_length=500)
    year       = models.PositiveIntegerField()
    category   = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='studies')
    study_type = models.CharField(max_length=50, choices=TYPE_CHOICES,
                                  default='Journal Article')
    status     = models.CharField(max_length=80, choices=STATUS_CHOICES,
                                  default='Legacy Study (Pre-Guidelines)')
    featured   = models.BooleanField(default=False)
    abstract   = models.TextField(blank=True)

    # PDF uploaded directly to Cloudinary (resource_type='raw' handles PDFs).
    pdf_file = CloudinaryField(
        'pdf_file',
        resource_type='raw',        # required for non-image files like PDFs
        folder='mvnp/repository',   # organises uploads inside Cloudinary
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.year} – {self.title[:80]}'

    @property
    def pdf_url(self):
        """Return a signed Cloudinary secure HTTPS URL for the PDF, or None."""
        if not self.pdf_file:
            return None
        # self.pdf_file is already a CloudinaryResource (parsed by from_db_value).
        # Use its public_id and resource_type directly instead of re-wrapping
        # str(self.pdf_file), which includes the "raw/upload/" prefix for new
        # uploads and would produce a broken double-prefixed URL.
        import cloudinary
        resource = self.pdf_file  # CloudinaryResource instance
        public_id = resource.public_id
        # Raw resources on Cloudinary keep the file extension as part of the
        # delivery path. If it's missing here, the generated URL 404s even
        # though the file exists (e.g. "mvnp/repository/abc123" instead of
        # "mvnp/repository/abc123.pdf").
        if not public_id.lower().endswith('.pdf'):
            public_id += '.pdf'
        return cloudinary.CloudinaryResource(
            public_id,
            resource_type=resource.resource_type or 'raw',
        ).build_url(secure=True, sign_url=True)

    class Meta:
        verbose_name_plural = 'Studies'
        ordering = ['-year', 'title']


class Keyword(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE,
                              related_name='keywords')
    word  = models.CharField(max_length=100)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word']


class ResearchApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending',  'Pending Review'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    ]

    user            = models.ForeignKey(User, on_delete=models.CASCADE,
                                        related_name='applications')
    applicant_name  = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    institution     = models.CharField(max_length=255)
    position        = models.CharField(max_length=255, blank=True)
    phone           = models.CharField(max_length=50,  blank=True)

    study_title         = models.CharField(max_length=500)
    research_category   = models.CharField(max_length=200, blank=True)
    research_location   = models.CharField(max_length=255, blank=True)
    proposed_start_date = models.DateField(null=True, blank=True)
    proposed_end_date   = models.DateField(null=True, blank=True)
    objectives          = models.TextField()
    summary             = models.TextField(blank=True)
    funding_source      = models.TextField(blank=True)

    # Supporting PDF uploaded directly to Cloudinary.
    supporting_documents = CloudinaryField(
        'supporting_documents',
        resource_type='raw',            # required for PDFs
        folder='mvnp/applications',     # organises uploads inside Cloudinary
        null=True,
        blank=True,
    )

    reviewer    = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    status       = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                    default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.study_title} by {self.applicant_name} ({self.status})'

    @property
    def document_url(self):
        """Return a signed Cloudinary secure HTTPS URL for the supporting document, or None."""
        if not self.supporting_documents:
            return None
        import cloudinary
        resource = self.supporting_documents  # CloudinaryResource instance
        public_id = resource.public_id
        if not public_id.lower().endswith('.pdf'):
            public_id += '.pdf'
        return cloudinary.CloudinaryResource(
            public_id,
            resource_type=resource.resource_type or 'raw',
        ).build_url(secure=True, sign_url=True)

    def send_status_notification(self):
        """Email the applicant when their application is approved or declined."""
        subject = f'MVNP Research Application {self.get_status_display()}'
        message = (
            f'Hello {self.applicant_name},\n\n'
            f'Your research application for "{self.study_title}" has been '
            f'{self.get_status_display().lower()}.\n\n'
            f'Status: {self.get_status_display()}\n'
            f'Reviewed by: {self.reviewer.get_full_name() or self.reviewer.username if self.reviewer else "MVNP staff"}\n'
            f'Reviewed at: {self.reviewed_at.strftime("%Y-%m-%d %H:%M:%S") if self.reviewed_at else "N/A"}\n\n'
            'Thank you for your interest in studying within MVNP.\n'
            'If you have any questions, please contact the research repository team.'
        )
        send_mail(
            subject,
            message,
            'no-reply@mvnp.gov.ph',
            [self.applicant_email],
            fail_silently=True,
        )

    def notify_mvnp_on_submission(self):
        """Email MVNP staff (mvnp@denr.gov.ph) when a new application is submitted."""
        mvnp_email = getattr(settings, 'MVNP_NOTIFICATION_EMAIL', 'mvnp@denr.gov.ph')
        doc_info = (
            f'Document (Cloudinary): {self.document_url}'
            if self.document_url else 'Document: None uploaded'
        )
        subject = f'New Research Application: {self.study_title}'
        message = (
            f'A new research application has been submitted to MVNP.\n\n'
            f'--- Applicant Details ---\n'
            f'Name:        {self.applicant_name}\n'
            f'Email:       {self.applicant_email}\n'
            f'Institution: {self.institution}\n'
            f'Position:    {self.position or "N/A"}\n'
            f'Phone:       {self.phone or "N/A"}\n\n'
            f'--- Research Details ---\n'
            f'Study Title:    {self.study_title}\n'
            f'Category:       {self.research_category or "N/A"}\n'
            f'Location:       {self.research_location or "N/A"}\n'
            f'Proposed Start: {self.proposed_start_date or "N/A"}\n'
            f'Proposed End:   {self.proposed_end_date or "N/A"}\n'
            f'Funding Source: {self.funding_source or "N/A"}\n\n'
            f'Objectives:\n{self.objectives}\n\n'
            f'Summary:\n{self.summary or "N/A"}\n\n'
            f'{doc_info}\n\n'
            f'Submitted at: {self.submitted_at.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            'Please log in to the MVNP Research Repository to review this application.'
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [mvnp_email],
            fail_silently=True,
        )

    class Meta:
        ordering = ['-submitted_at']