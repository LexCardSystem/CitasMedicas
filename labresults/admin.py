from django.contrib import admin
from .models import (
    LabTestDefinition, LabTestNumericRange, LabTestListItem,
    PatientLabResult, PatientLabResultValue
)

class LabTestNumericRangeInline(admin.TabularInline):
    model = LabTestNumericRange
    extra = 1

class LabTestListItemInline(admin.TabularInline):
    model = LabTestListItem
    extra = 1

@admin.register(LabTestDefinition)
class LabTestDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_link', 'result_type')
    list_filter = ('result_type',)
    search_fields = ('name',)
    inlines = [LabTestNumericRangeInline, LabTestListItemInline]

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj: # Only show relevant inlines based on result_type
            if obj.result_type == 'NUMERIC':
                inlines.append(LabTestNumericRangeInline(self.model, self.admin_site))
            elif obj.result_type == 'LIST':
                inlines.append(LabTestListItemInline(self.model, self.admin_site))
        # If obj is None (creating new), show all initially or none, depending on preference.
        # Current behavior: shows none for new. To show all for new, remove the outer "if obj:"
        # and handle obj=None inside the conditions or just add all inlines.
        # For this setup, showing specific inlines on existing objects is the main goal.
        # To show all inlines when obj is None (i.e. on the 'add' page before type is chosen):
        # else:
        #     return [inline(self.model, self.admin_site) for inline in self.inlines]
        return inlines


class PatientLabResultValueInline(admin.TabularInline):
    model = PatientLabResultValue
    extra = 1
    # Consider raw_id_fields for ForeignKey if lists get long
    raw_id_fields = ('numeric_range_item_tested', 'list_value_selected')
    # Make parameter_name_display readonly if it's auto-populated effectively
    # readonly_fields = ('parameter_name_display', 'is_abnormal')


@admin.register(PatientLabResult)
class PatientLabResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test_definition', 'appointment', 'collection_datetime', 'reported_datetime', 'status')
    list_filter = ('status', 'test_definition', 'reported_datetime')
    search_fields = ('patient__username', 'test_definition__name', 'appointment__appointment_code')
    raw_id_fields = ('patient', 'appointment', 'test_definition')
    inlines = [PatientLabResultValueInline]
    # readonly_fields = ('status',) # If status is derived from values

# admin.site.register(PatientLabResultValue) # Usually managed via inline
