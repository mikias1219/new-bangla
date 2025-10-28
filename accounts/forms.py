from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Organization

class UserRegistrationForm(UserCreationForm):
    """User registration form"""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False, help_text="Optional phone number")
    organization_name = forms.CharField(max_length=255, required=False, help_text="Your organization name (optional)")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'organization_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')

        # Automatically assign to the default organization
        try:
            default_org = Organization.objects.filter(is_active=True).first()
            if default_org:
                user.organization = default_org
        except Organization.DoesNotExist:
            pass  # Will handle this in the view

        if commit:
            user.save()
        return user

class UserProfileForm(UserChangeForm):
    """User profile update form"""

    password = None  # Remove password field

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'avatar', 'language')
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class OrganizationForm(forms.ModelForm):
    """Organization form"""

    class Meta:
        model = Organization
        fields = ('name', 'description', 'website', 'logo', 'contact_email', 'contact_phone',
                 'subscription_plan', 'max_users', 'max_conversations')
        widgets = {
            'logo': forms.FileInput(attrs={'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
