from django.shortcuts import render
from django.views import generic
from . import forms
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView


# Create your views here.


class Index(generic.View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'index.html')


#
#
class CustomLoginView(LoginView):
    form_class = forms.EmailAuthenticationForm
    template_name = 'registration/login.html'

