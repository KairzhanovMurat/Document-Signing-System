from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import generic

from . import models


# Create your views here.


class Index(generic.View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'index.html')


class UploadFileView(LoginRequiredMixin, generic.CreateView):
    model = models.Document
    template_name = 'create.html'
    fields = ('file', 'description')

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateFileView(LoginRequiredMixin, generic.UpdateView):
    model = models.Document
    template_name = 'update.html'
    fields = ('file', 'description')

    def get_success_url(self):
        return self.object.get_absolute_url()


class DeleteFileView(LoginRequiredMixin, generic.DeleteView):
    model = models.Document
    template_name = 'delete.html'
    success_url = '/list'


class ListFileView(LoginRequiredMixin, generic.ListView):
    model = models.Document
    template_name = 'list.html'
    context_object_name = 'files'

    def get_queryset(self):
        return models.Document.objects.filter(user=self.request.user).all()


class DetailFileView(LoginRequiredMixin, generic.DetailView):
    model = models.Document
    template_name = 'detail.html'


class CreateApprovalRequest(LoginRequiredMixin, generic.View):
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
        document.is_approved = False
        document.save()
        approval_request = models.ApprovalRequest.objects.create(sender=sender, document=document)
        approval_request.receivers.set(receivers)
        approval_request.initial_receivers.set(receivers)
        approval_request.save()
        return redirect('home')


class ListApprovalRequest(LoginRequiredMixin, generic.ListView):
    template_name = 'list_approval.html'
    model = models.ApprovalRequest
    context_object_name = 'approval_requests'

    def get_queryset(self):
        return models.ApprovalRequest.objects.filter(sender=self.request.user).select_related('document')


class IncomingApprovals(LoginRequiredMixin, generic.ListView):
    model = models.ApprovalRequest
    context_object_name = 'approvals'
    template_name = 'incoming_approvals.html'

    def get_queryset(self):
        user_id = self.request.user.id
        return models.ApprovalRequest.objects.filter(receivers=user_id).select_related('document', 'sender')


def approve_request(request, approval_request_pk):
    if request.method == 'POST':
        user_id = request.user.id
        approval_request = models.ApprovalRequest.objects.filter(pk=approval_request_pk).first()
        approval_request.receivers.remove(user_id)
        approval_request.save()
        if approval_request.receivers.count() == 0:
            doc = approval_request.document
            doc.is_approved = True
            approval_request.is_approved = True
            approval_request.save()
            doc.save()
        return redirect('incoming_approvals')
