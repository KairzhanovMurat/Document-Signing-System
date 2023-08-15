from django import forms
from django.contrib.auth import get_user_model

from . import models


class SharingRequestForm(forms.ModelForm):
    sender = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.Select,
        required=True,
        help_text="Select the sender of the approval request."
    )

    class Meta:
        model = models.ApprovalRequest
        fields = ['sender', 'receivers']

    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)  # Remove 'sender' from kwargs if present
        super().__init__(*args, **kwargs)
        if sender:
            self.fields['sender'].queryset = get_user_model().objects.filter(id=sender.id)

    def save(self, commit=True):
        sharing_request = super().save(commit=False)
        sharing_request.sender = self.cleaned_data['sender']
        if commit:
            sharing_request.save()
            sharing_request.receivers.add(*self.cleaned_data['receivers'])
        return sharing_request
