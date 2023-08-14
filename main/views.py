from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views import generic
from . import models
from . import forms


# Create your views here.


class Index(generic.View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'index.html')


#
#
# class CustomLoginView(LoginView):
#     # form_class = forms.EmailAuthenticationForm
#     template_name = 'registration/login.html'


class UploadFileView(generic.CreateView):
    model = models.Document
    template_name = 'create.html'
    success_url = '/'
    fields = ('file', 'description')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateFileView(generic.UpdateView):
    model = models.Document
    template_name = 'update.html'
    fields = ('file', 'description')

    def get_success_url(self):
        return self.object.get_absolute_url()


class DeleteFileView(generic.DeleteView):
    model = models.Document
    template_name = 'delete.html'
    success_url = '/list'


class ListFileView(generic.ListView):
    model = models.Document
    template_name = 'list.html'
    context_object_name = 'files'

    def get_queryset(self):
        return models.Document.objects.filter(user=self.request.user).all()


class DetailFileView(generic.DetailView):
    model = models.Document
    template_name = 'detail.html'
