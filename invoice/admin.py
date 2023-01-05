from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from django.apps import apps
app_dict=apps.all_models['invoice']
model_list=[v for v in app_dict.values()]

@admin.register(*model_list)
class ViewAdmin(ImportExportModelAdmin):
	pass
