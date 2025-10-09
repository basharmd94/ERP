from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Business, UserBusinessAccess


class ZidLoginForm(AuthenticationForm):
    """
    Custom login form that includes ZID field
    """
    zid = forms.CharField(
        label="Business ID",
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Business ID (ZID)'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the default widgets with Bootstrap classes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })


class UserBusinessForm(forms.Form):
    """
    Form for admin to assign businesses to users
    """
    user = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        label="User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    businesses = forms.ModelMultipleChoiceField(
        queryset=Business.objects.filter(is_active=True),
        label="Businesses",
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        from django.contrib.auth.models import User
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()


class RegisterUserForm(UserCreationForm):
    """
    Form for admin to create a new user and assign businesses
    """
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap styling
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })
