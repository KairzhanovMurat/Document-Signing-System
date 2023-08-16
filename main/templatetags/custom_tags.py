from django import template
from main.models import ApprovalRequest

register = template.Library()


@register.simple_tag
def incoming_approvals_badge(user):
    user_id = user.id
    approvals_count = ApprovalRequest.objects.filter(receivers=user_id).select_related('document',
                                                                                       'sender').count()
    return approvals_count
