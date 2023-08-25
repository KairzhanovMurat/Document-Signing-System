from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.views import generic

from . import forms
from . import models
from . import utils


# Create your views here.


class Index(generic.View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'index.html')


class UploadFileView(LoginRequiredMixin, generic.CreateView):
    model = models.Document
    template_name = 'create_doc.html'
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['requests_count'] = self.object.approval_requests.count()
        return context


class DeleteFileView(LoginRequiredMixin, generic.DeleteView):
    model = models.Document
    template_name = 'delete_doc.html'
    success_url = '/doc/list'


class ListFileView(LoginRequiredMixin, generic.ListView):
    model = models.Document
    template_name = 'doc_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        return models.Document.objects.filter(user=self.request.user).all()


class DetailFileView(LoginRequiredMixin, generic.DetailView):
    model = models.Document
    template_name = 'doc_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['requests_count'] = self.object.approval_requests.count()
        return context


class CreateApprovalRequest(LoginRequiredMixin, generic.CreateView):
    model = models.ApprovalRequest
    template_name = 'create_approval.html'
    form_class = forms.ApprovalRequestForm

    def get_success_url(self):
        return reverse('approvals_history')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.save()
        return super().form_valid(form)


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
        return (models.ApprovalRequest.objects.filter(receivers=user_id, requestreceivers__is_approved=False).
                select_related('document', 'sender'))


@login_required
def search(request):
    search_input = request.GET.get('documents') or ''
    if search_input:
        try:
            queryset = models.Document.objects.filter(description__istartswith=search_input, user=request.user)
            return render(request, 'search_results.html', context={'qs': queryset})
        except AttributeError:
            pass


@transaction.atomic
def approve_request(request, approval_request_pk):
    if request.method == 'POST':
        request_receiver = models.RequestReceivers.objects.filter(request_id=approval_request_pk,
                                                                  receivers=request.user).first()
        request_receiver.is_approved = True
        request_receiver.save()

        approval_request = models.ApprovalRequest.objects.filter(pk=approval_request_pk).first()

        user_browser = request.META.get('HTTP_USER_AGENT', 'Unknown Browser')
        user_ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
        user_time = timezone.now()

        user_approval_data = models.UserApprovalData(
            user=request.user,
            approval_request=approval_request,
            browser=user_browser,
            ip_address=user_ip,
            approval_time=user_time
        )
        user_approval_data.save()

        if models.RequestReceivers.are_all_approved(approval_request):
            payload = utils.get_approval_data_dict(request_id=approval_request.id)

            doc_path = approval_request.document.file.path
            signed_doc_path = doc_path
            header_content = f"""
                       <p>ЛИСТ СОГЛАСОВАНИЯ</p>
                       <p>к {approval_request.document.description} от {approval_request.requested_at.
            strftime('%Y-%m-%d')}</p>
                       """

            td = utils.get_table_data(request_id=approval_request.id)
            utils.generate_pdf_with_qr(doc_path, signed_doc_path, header_content, td, payload)

            doc = approval_request.document
            doc.is_approved = True
            approval_request.is_approved = True
            approval_request.save()
            doc.save()

        return redirect('incoming_approvals')
