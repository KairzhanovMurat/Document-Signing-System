from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from . import models


# class EmailAuthenticationForm(AuthenticationForm):
#     email = forms.EmailField(label='Email', max_length=254)
#
#     def clean(self):
#         email = self.cleaned_data.get('email')
#         password = self.cleaned_data.get('password')
#
#         if email and password:
#             self.user_cache = authenticate(self.request, email=email, password=password)
#             if self.user_cache is None:
#                 raise forms.ValidationError('Invalid email or password')
#         return self.cleaned_data


class FileUploadForm(ModelForm):
    class Meta:
        model = models.Document
        fields = ('file', 'description')
