from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, DiagnosisRecord

# 1. Register the Custom User Model
# We extend the base UserAdmin to show our 'role' field in the admin panel
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)

# 2. Register Patient Profile
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'blood_group', 'created_at')
    search_fields = ('user__username', 'blood_group')
    list_filter = ('gender', 'blood_group')

# 3. Register Diagnosis Records
@admin.register(DiagnosisRecord)
class DiagnosisRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'result_diagnosis', 'confidence_score', 'timestamp')
    search_fields = ('patient__user__username', 'result_diagnosis')
    list_filter = ('result_diagnosis', 'timestamp')
    readonly_fields = ('timestamp',) # Keeps the time uneditable for medical integrity