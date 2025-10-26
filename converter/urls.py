from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('convert/<str:conversion_type>/', views.convert_file, name='convert_file'),
    
    # API endpoints
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/status/<uuid:conversion_id>/', views.conversion_status, name='conversion_status'),
    path('api/download/<uuid:conversion_id>/', views.download_file, name='download_file'),
    path('api/history/', views.conversion_history, name='conversion_history'),
    path('api/delete/<uuid:conversion_id>/', views.delete_conversion, name='delete_conversion'),
]

