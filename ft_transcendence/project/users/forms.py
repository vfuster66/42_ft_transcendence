
# users/forms.py

#########################################################################################################

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm

#########################################################################################################

class CustomAuthenticationForm(AuthenticationForm):
    token = forms.CharField(label="2FA Token", required=False)

def __init__(self, request=None, *args, **kwargs):
    super(CustomAuthenticationForm, self).__init__(request=request, *args, **kwargs)
    self.fields['token'].widget.attrs['class'] = 'form-control'

#########################################################################################################

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='')
    consent = forms.BooleanField(
        required=True,
        label=_("I accept the terms and conditions and the privacy policy.")
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'consent')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

#########################################################################################################

class UserForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, required=True, help_text=_("Required. Please enter a valid email address."))

    class Meta:
        model = User
        fields = ('email',)

#########################################################################################################

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, label=_("First name"))
    last_name = forms.CharField(max_length=100, label=_("Last name"))
    location = forms.CharField(max_length=100, label=_("Location"))
    status = forms.CharField(max_length=100, label=_("Status"))
    bio = forms.CharField(widget=forms.Textarea, label=_("Biography"))
    email = forms.EmailField(max_length=254, required=True, help_text=_("Required. Please enter a valid email address."))

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'location', 'status', 'bio', 'avatar')
        widgets = {
            'status': forms.TextInput(attrs={'class': 'status-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email if self.user else None

        order = ['first_name', 'last_name', 'email', 'location', 'status', 'bio', 'avatar']
        for key in order:
            self.fields[key].widget.attrs.update({'class': 'form-control'})
        self.order_fields(order)

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 500:
            raise ValidationError(_("The bio cannot contain more than 500 characters."))
        return bio

    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
                profile.save()
        return profile
  
#########################################################################################################

