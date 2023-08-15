from django.shortcuts import render, redirect
from django.views import generic

from . import models


# Create your views here.


class Index(generic.View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'index.html')


class UploadFileView(generic.CreateView):
    model = models.Document
    template_name = 'create.html'
    success_url = '/list'
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


class CreateApprovalRequest(generic.View):
    template_name = 'approval.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        receivers = models.DefaultUser.objects.exclude(id=user.id)
        documents = models.Document.objects.filter(user=user)
        context = {'receivers': receivers, 'documents': documents}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        sender = request.user
        receivers = request.POST.getlist('receivers')
        document_id = request.POST.get('document')
        document = models.Document.objects.get(id=document_id)
        approval_request = models.ApprovalRequest.objects.create(sender=sender, document=document)
        approval_request.receivers.set(receivers)
        approval_request.save()
        return redirect('home')


class ListApprovalRequest(generic.ListView):
    template_name = 'list_approval.html'
    model = models.ApprovalRequest
    context_object_name = 'approval_requests'

    def get_queryset(self):
        return models.ApprovalRequest.objects.filter(sender=self.request.user).select_related('document', 'sender')
