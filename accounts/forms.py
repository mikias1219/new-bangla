from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Organization

class UserRegistrationForm(UserCreationForm):
    """User registration form"""

    email = forms.EmailField(required=True)
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(is_active=True),
        required=True,
        empty_label="Select Organization"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'organization', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.organization = self.cleaned_data['organization']
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
