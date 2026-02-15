from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import MedicalLog, MedicalDocument
from .forms import MedicalLogForm, MedicalDocumentForm
from itertools import chain
from operator import attrgetter


# 🔒 Mixin to allow only patients
class PatientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "PATIENT"

    def handle_no_permission(self):
        return redirect("home")


# Add Log
class AddLogView(LoginRequiredMixin, PatientRequiredMixin, CreateView):
    model = MedicalLog
    form_class = MedicalLogForm
    template_name = "medical_history/add_log.html"
    success_url = reverse_lazy("medical_history:view_logs")

    def form_valid(self, form):
        form.instance.patient = self.request.user
        return super().form_valid(form)


# View Logs
class ViewLogsView(LoginRequiredMixin, PatientRequiredMixin, ListView):
    model = MedicalLog
    template_name = "medical_history/view_logs.html"
    context_object_name = "logs"

    def get_queryset(self):
        return MedicalLog.objects.filter(patient=self.request.user)


# Upload Document
class UploadDocumentView(LoginRequiredMixin, PatientRequiredMixin, CreateView):
    model = MedicalDocument
    form_class = MedicalDocumentForm
    template_name = "medical_history/upload_document.html"
    success_url = reverse_lazy("medical_history:view_documents")

    def form_valid(self, form):
        form.instance.patient = self.request.user
        return super().form_valid(form)


# View Documents
class ViewDocumentsView(LoginRequiredMixin, PatientRequiredMixin, ListView):
    model = MedicalDocument
    template_name = "medical_history/view_documents.html"
    context_object_name = "documents"

    def get_queryset(self):
        return MedicalDocument.objects.filter(patient=self.request.user)

class MedicalHistoryDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "medical_history/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        logs = MedicalLog.objects.filter(patient=self.request.user)
        documents = MedicalDocument.objects.filter(patient=self.request.user)

        # Combine and sort by datetime
        combined = sorted(
            chain(logs, documents),
            key=attrgetter('created_at'),
            reverse=True
        )

        context['records'] = combined
        return context
    

# update and delete operations:

class UpdateLogView(LoginRequiredMixin, UpdateView):
    model = MedicalLog
    form_class = MedicalLogForm
    template_name = "medical_history/add_log.html"
    success_url = reverse_lazy("medical_history:dashboard")
    def get_queryset(self):
        return self.model.objects.filter(patient=self.request.user)


class UpdateDocumentView(LoginRequiredMixin, UpdateView):
    model = MedicalDocument
    form_class = MedicalDocumentForm
    template_name = "medical_history/upload_document.html"
    success_url = reverse_lazy("medical_history:dashboard")
    def get_queryset(self):
        return self.model.objects.filter(patient=self.request.user)


class DeleteLogView(LoginRequiredMixin, View):
    def post(self, request, pk):
        log = get_object_or_404(MedicalLog, pk=pk, patient=request.user)
        log.delete()
        return redirect("medical_history:dashboard")


class DeleteDocumentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        document = get_object_or_404(MedicalDocument, pk=pk, patient=request.user)
        document.delete()
        return redirect("medical_history:dashboard")
