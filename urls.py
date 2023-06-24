from django.urls import path, re_path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.InboxView.as_view(), name='messages_list'),
    path('<str:id>/', views.ThreadView.as_view(), name='thread_messages'),
    path('file/upload/<str:id>/', views.UploadFile.as_view(), name='upload_file')
]
