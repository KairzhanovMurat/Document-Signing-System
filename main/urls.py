from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('create', views.UploadFileView.as_view(), name='create'),
    path('update/<int:pk>', views.UpdateFileView.as_view(), name='update'),
    path('delete/<int:pk>', views.DeleteFileView.as_view(), name='delete'),
    path('list', views.ListFileView.as_view(), name='list'),
    path('detail/<int:pk>', views.DetailFileView.as_view(), name='detail')
]
