from django.contrib import admin
from .models import Attendance, AttendanceDetail, Role, RunType, Guild, CutDistribution, CutInIR
from unfold.admin import ModelAdmin,TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.forms import UserCreationForm
@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ['date_time', 'status', 'total_pot']

@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ['name', 'value']

@admin.register(RunType)
class RunTypeAdmin(ModelAdmin):
    list_display = ['name', 'value']

@admin.register(CutInIR)
class CutInIR(ModelAdmin):
    list_display = ['amount']