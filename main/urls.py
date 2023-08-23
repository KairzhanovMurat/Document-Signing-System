from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('doc/create', views.UploadFileView.as_view(), name='create'),
    path('doc/update/<int:pk>', views.UpdateFileView.as_view(), name='update'),
    path('doc/delete/<int:pk>', views.DeleteFileView.as_view(), name='delete'),
    path('doc/list', views.ListFileView.as_view(), name='list'),
    path('doc/detail/<int:pk>', views.DetailFileView.as_view(), name='detail'),
    path('doc/search', views.search, name='search'),
    path('approvals/create', views.CreateApprovalRequest.as_view(), name='approval'),
    path('approvals/list', views.ListApprovalRequest.as_view(), name='approval_list'),
    path('approvals/incoming', views.IncomingApprovals.as_view(), name='incoming_approvals'),
    path('approvals/approve/<int:approval_request_pk>/', views.approve_request, name='approve_request'),
]
