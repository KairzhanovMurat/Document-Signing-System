from django import template
from main.models import ApprovalRequest

register = template.Library()


@register.filter
def incoming_approvals_badge(user):
    user_id = user.id
    approvals_count = ApprovalRequest.objects.filter(receivers=user_id).count()
    return approvals_count
