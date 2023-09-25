from django.db.models import Q, OuterRef, Exists
from django import forms
from . import models  # Import your models module


class ApprovalRequestForm(forms.ModelForm):
    class Meta:
        model = models.ApprovalRequest
        fields = ('document',)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a subquery to check if there are related approval requests for the document
        subquery = models.ApprovalRequest.objects.filter(
            document=OuterRef('pk'),
            is_approved=False
        ).values('document')

        # Use the subquery to filter documents with associated approval requests (is_approved=False)
        # or documents with no associated approval requests
        self.fields['document'].queryset = models.Document.objects.filter(
            user=user
        ).annotate(has_approval_request=Exists(subquery)).exclude(
            Q(has_approval_request=True) | Q(is_approved=True)
        )
