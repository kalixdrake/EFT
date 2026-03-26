from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('api/', views.chat_api, name='chat_api'),
]
