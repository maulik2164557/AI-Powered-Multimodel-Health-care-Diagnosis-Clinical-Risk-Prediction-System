from django.urls import path
from .views import (
    AddLogView,
    ViewLogsView,
    UploadDocumentView,
    ViewDocumentsView,
    MedicalHistoryDashboardView,
    UpdateLogView,
    DeleteLogView,
    UpdateDocumentView,
    DeleteDocumentView,
)

app_name = 'medical_history'

urlpatterns = [
    path('', MedicalHistoryDashboardView.as_view(), name='dashboard'),

    # Create
    path('logs/add/', AddLogView.as_view(), name='add_log'),
    path('documents/upload/', UploadDocumentView.as_view(), name='upload_document'),

    # List (optional now since you unified)
    path('logs/', ViewLogsView.as_view(), name='view_logs'),
    path('documents/', ViewDocumentsView.as_view(), name='view_documents'),

    # Update
    path('logs/<int:pk>/update/', UpdateLogView.as_view(), name='update_log'),
    path('documents/<int:pk>/update/', UpdateDocumentView.as_view(), name='update_document'),

    # Delete
    path('logs/<int:pk>/delete/', DeleteLogView.as_view(), name='delete_log'),
    path('documents/<int:pk>/delete/', DeleteDocumentView.as_view(), name='delete_document'),
]
