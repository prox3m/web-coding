from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('files/', views.file_list, name='file_list'),
    path('database/', views.db_list, name='db_list'),
    path('api/search/', views.ajax_search, name='ajax_search'),
    path('database/edit/<int:pk>/', views.edit_record, name='edit_record'),
    path('database/delete/<int:pk>/', views.delete_record, name='delete_record'),
]