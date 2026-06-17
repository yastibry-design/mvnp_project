from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from .models import Study, ResearchApplication


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = [
            'study_id',
            'title',
            'authors',
            'year',
            'category',
            'study_type',
            'status',
            'featured',
            'abstract',
            'pdf_file',
        ]
        widgets = {
            'abstract': forms.Textarea(attrs={'rows': 5}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'is_active',
            'is_staff',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'user@example.com'}),
        }


class ResearchApplicationForm(forms.ModelForm):
    class Meta:
        model = ResearchApplication
        fields = [
            'applicant_name',
            'applicant_email',
            'institution',
            'position',
            'phone',
            'study_title',
            'research_category',
            'research_location',
            'proposed_start_date',
            'proposed_end_date',
            'objectives',
            'summary',
            'funding_source',
            'supporting_documents',
        ]
        widgets = {
            'applicant_name': forms.TextInput(attrs={'placeholder': 'Full name of the lead researcher'}),
            'applicant_email': forms.EmailInput(attrs={'placeholder': 'name@institution.edu'}),
            'institution': forms.TextInput(attrs={'placeholder': 'University, research institute, or agency'}),
            'position': forms.TextInput(attrs={'placeholder': 'Position or role'}),
            'phone': forms.TextInput(attrs={'placeholder': '+63 912 345 6789'}),
            'research_category': forms.TextInput(attrs={'placeholder': 'Ecology, Conservation, Biodiversity, etc.'}),
            'research_location': forms.TextInput(attrs={'placeholder': 'MVNP site, barangay, habitat area'}),
            'proposed_start_date': forms.DateInput(attrs={'type': 'date'}),
            'proposed_end_date': forms.DateInput(attrs={'type': 'date'}),
            'objectives': forms.Textarea(attrs={'rows': 4}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'funding_source': forms.Textarea(attrs={'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    """Lets any logged-in user update their display name and email."""
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
        }


class ProfilePasswordChangeForm(DjangoPasswordChangeForm):
    """Thin wrapper so we can style it consistently with Bootstrap-free CSS."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(
            attrs={'placeholder': 'Current password', 'autocomplete': 'current-password'}
        )
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={'placeholder': 'New password', 'autocomplete': 'new-password'}
        )
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={'placeholder': 'Confirm new password', 'autocomplete': 'new-password'}
        )
