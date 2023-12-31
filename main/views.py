from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic

from . import forms
from . import models
from . import utils

# Create your views here.

User = get_user_model()


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

    @transaction.atomic
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateFileView(LoginRequiredMixin, generic.UpdateView):
    model = models.Document
    template_name = 'update.html'
    fields = ('file', 'description')

    @transaction.atomic
    def form_valid(self, form):
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.user != self.request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['requests_count'] = self.object.approval_requests.count()
        return context


class DeleteFileView(LoginRequiredMixin, generic.DeleteView):
    model = models.Document
    template_name = 'delete_doc.html'
    success_url = reverse_lazy('list_doc')

    def dispatch(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.user != self.request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


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

    def dispatch(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.user != self.request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['requests_count'] = self.object.approval_requests.count()
        return context


class CreateApprovalRequest(LoginRequiredMixin, generic.CreateView):
    model = models.ApprovalRequest
    template_name = 'create_approval.html'
    form_class = forms.ApprovalRequestForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


@login_required
@transaction.atomic
def update_approval(request, pk):
    approval = models.ApprovalRequest.objects.get(pk=pk)
    context = dict()
    context['all_receivers'] = User.objects.exclude(pk=request.user.pk)
    context['approval_receivers'] = approval.receivers.all()
    context['approval'] = approval
    context['receiver_not_found'] = False
    context['document'] = approval.document

    if request.method == 'POST':
        receiver_second_name = request.POST['receiver_name']
        receiver = User.objects.filter(second_name=receiver_second_name).first()
        doc = approval.document
        sender = approval.sender
        if receiver and receiver.id != request.user.id and receiver not in approval.receivers.all():
            models.RequestReceivers.objects.create(receivers_id=receiver.id, request_id=approval.id)
            try:
                utils.send_notification_email(sender=sender, receiver=receiver, document=doc)
            except:
                pass

        else:
            context['receiver_not_found'] = True
    return render(request, 'update_approval.html', context=context)


@transaction.atomic
def delete_approval(request, pk):
    approval = models.ApprovalRequest.objects.get(pk=pk)
    approval.delete()
    return redirect('approval_create')


@transaction.atomic
def delete_receiver(request, request_id, receiver_id):
    receiver = models.RequestReceivers.objects.filter(request_id=request_id, receivers=receiver_id).first()
    receiver.delete()
    return redirect(reverse('update_approval', args=[str(request_id)]))


class ListApprovalRequest(LoginRequiredMixin, generic.ListView):
    template_name = 'list_approval.html'
    model = models.ApprovalRequest
    context_object_name = 'approval_requests'

    def get_queryset(self):
        return models.ApprovalRequest.objects.filter(sender=self.request.user).select_related('document')


class ApprovalRequestDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'sender_approval_detail.html'
    model = models.ApprovalRequest
    context_object_name = 'approval'

    def dispatch(self, request, *args, **kwargs):
        approval = self.get_object()
        if approval.sender != self.request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        approval = self.get_object()
        ctxt = super().get_context_data()
        ctxt['approved_receivers'] = models.RequestReceivers.objects.filter(request_id=approval.id, is_approved=True)
        ctxt['all_receivers'] = models.RequestReceivers.objects.filter(request_id=approval.id, is_approved=False,
                                                                       is_disapproved=False)
        ctxt['rejected_receivers'] = models.RequestReceivers.objects.filter(request_id=approval.id, is_disapproved=True)
        ctxt['is_rejected'] = bool(
            models.RequestReceivers.objects.filter(request_id=approval.id, is_disapproved=True).count())
        return ctxt


class IncomingApprovals(LoginRequiredMixin, generic.ListView):
    model = models.ApprovalRequest
    context_object_name = 'approvals'
    template_name = 'incoming_approvals.html'

    def get_queryset(self):
        user_id = self.request.user.id
        return (models.ApprovalRequest.objects.filter(receivers=user_id, requestreceivers__is_approved=False,
                                                      requestreceivers__is_disapproved=False).
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
                       <p>к документу '{approval_request.document.description}' от {approval_request.requested_at.
            strftime('%Y-%m-%d')}</p>
                       """
            td = utils.get_table_data(sender=approval_request.sender,
                                      request_id=approval_request.id)

            utils.generate_pdf_with_qr(doc_path, signed_doc_path, header_content, td, payload)

            doc = approval_request.document
            doc.is_approved = True
            approval_request.is_approved = True
            approval_request.save()
            doc.save()
            try:
                utils.send_success_email(approval_request.sender, approval_request.document)
            except:
                pass
        return redirect('incoming_approvals')


class ApprovalsHistoryView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'approvals'
    model = models.UserApprovalData
    template_name = 'approvals_history.html'

    def get_queryset(self):
        user_id = self.request.user.id
        return self.model.objects.filter(user_id=user_id).select_related('approval_request',
                                                                         'approval_request__document')


class ApprovalDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.UserApprovalData
    template_name = 'approval_detail.html'
    context_object_name = 'approval'

    def dispatch(self, request, *args, **kwargs):
        approval = self.get_object()
        if approval.user != self.request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


@login_required
@transaction.atomic
def reject_approval(request, request_id):
    receiver_id = request.user.id
    receiver = models.RequestReceivers.objects.filter(request_id=request_id, receivers=receiver_id).first()
    if request.method == 'POST':
        comment = request.POST.get('comment')
        receiver.comment = comment
        receiver.is_disapproved = True
        receiver.save()
        return redirect('incoming_approvals')
    return render(request, 'comment_page.html')


def custom_404_view(request, exception):
    return render(request, 'exception_pages/404.html', status=404)


def custom_500_view(request):
    return render(request, 'exception_pages/500.html', status=500)
