from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from django.conf.urls import handler404, handler500

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('doc/create', views.UploadFileView.as_view(), name='create_doc'),
    path('doc/update/<int:pk>', views.UpdateFileView.as_view(), name='update_doc'),
    path('doc/delete/<int:pk>', views.DeleteFileView.as_view(), name='delete_doc'),
    path('doc/list', views.ListFileView.as_view(), name='list_doc'),
    path('doc/detail/<int:pk>', views.DetailFileView.as_view(), name='detail_doc'),
    path('doc/search', views.search, name='search_doc'),
    path('approvals/create', views.CreateApprovalRequest.as_view(), name='approval_create'),
    path('approvals/list', views.ListApprovalRequest.as_view(), name='approvals_history'),
    path('approvals/incoming', views.IncomingApprovals.as_view(), name='incoming_approvals'),
    path('approvals/approve/<int:approval_request_pk>/', views.approve_request, name='approve_request'),
    path('approvals/history', views.ApprovalsHistoryView.as_view(), name='signed_approvals_history')
]

handler404 = views.custom_404_view
handler500 = views.custom_500_view
