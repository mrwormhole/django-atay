from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserSignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

        self.fields['password1'].help_text = "Your password should be at least 8 characters with numbers and letters"
        self.fields['password2'].help_text = None

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email',]
        required = ['first_name', 'last_name', 'email']
        