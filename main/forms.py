from django import forms
from django.contrib.auth import get_user_model

from . import models


class ApprovalRequestForm(forms.ModelForm):
    class Meta:
        model = models.ApprovalRequest
        fields = ('document',)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].queryset = models.Document.objects.select_related('user').filter(user=user,
                                                                                                 is_approved=False)
