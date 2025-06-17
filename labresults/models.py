from django.db import models
from django.conf import settings # For Patient
from scheduling.models import Service, Appointment # For linking
import uuid

class LabTestDefinition(models.Model):
    RESULT_TYPES = [
        ('NUMERIC', 'Numeric'),
        ('LIST', 'List-based'),
        ('TEXT', 'Descriptive Text'),
    ]
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    # The specific lab service that needs to be booked
    service_link = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,
                                     help_text='The lab service that must be booked for this test definition.')
    result_type = models.CharField(max_length=10, choices=RESULT_TYPES)

    def __str__(self):
        return f'{self.name} ({self.get_result_type_display()})'

class LabTestNumericRange(models.Model):
    '''Defines a specific parameter within a NUMERIC type LabTestDefinition, with its reference range.'''
    test_definition = models.ForeignKey(LabTestDefinition, on_delete=models.CASCADE, related_name='numeric_ranges',
                                        limit_choices_to={'result_type': 'NUMERIC'})
    parameter_name = models.CharField(max_length=100, help_text='e.g., Hemoglobin, Glucose')
    unit = models.CharField(max_length=50, blank=True, help_text='e.g., g/dL, mg/dL')
    lower_bound_normal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    upper_bound_normal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    notes_for_range = models.CharField(max_length=255, blank=True, help_text='Optional notes, e.g., Varies with age/gender')

    class Meta:
        unique_together = ('test_definition', 'parameter_name')

    def __str__(self):
        return f'{self.test_definition.name} - {self.parameter_name} ({self.lower_bound_normal}-{self.upper_bound_normal} {self.unit})'

class LabTestListItem(models.Model):
    '''Defines a possible value for a LIST type LabTestDefinition.'''
    test_definition = models.ForeignKey(LabTestDefinition, on_delete=models.CASCADE, related_name='list_items',
                                        limit_choices_to={'result_type': 'LIST'})
    item_value = models.CharField(max_length=100, help_text='e.g., Positive, Negative, A+, Clear')
    is_normal_value = models.BooleanField(default=True, help_text='Is this list item considered a normal finding?')

    class Meta:
        unique_together = ('test_definition', 'item_value')

    def __str__(self):
        return f'{self.test_definition.name} - Option: {self.item_value} (Normal: {self.is_normal_value})'

class PatientLabResult(models.Model):
    '''Represents an instance of a lab test performed for a patient.'''
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_results')
    # The appointment during which sample was collected or test was ordered/performed
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_results')
    test_definition = models.ForeignKey(LabTestDefinition, on_delete=models.PROTECT, help_text='The type of lab test performed.')
    # sample_id = models.CharField(max_length=50, blank=True, help_text='Internal lab sample identifier')
    collection_datetime = models.DateTimeField(null=True, blank=True, help_text='Date and time of sample collection.')
    reported_datetime = models.DateTimeField(null=True, blank=True, help_text='Date and time result was reported.')
    notes_overall = models.TextField(blank=True, help_text='Overall comments on this lab test instance by lab staff.')
    # Status: e.g., PENDING, PARTIAL, COMPLETE, CANCELLED
    STATUS_CHOICES = [('PENDING', 'Pending'), ('PARTIAL', 'Partial'), ('COMPLETE', 'Complete'), ('CANCELLED', 'Cancelled')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')


    def __str__(self):
        return f'Lab Result for {self.patient.username} - {self.test_definition.name} (Appt: {self.appointment_id})'

class PatientLabResultValue(models.Model):
    '''Stores a specific value for a parameter within a PatientLabResult.'''
    lab_result = models.ForeignKey(PatientLabResult, on_delete=models.CASCADE, related_name='values')

    # For NUMERIC type: which specific numeric parameter this value is for
    numeric_range_item_tested = models.ForeignKey(LabTestNumericRange, null=True, blank=True, on_delete=models.PROTECT,
                                               help_text='Links to the specific numeric parameter definition.')
    numeric_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    # For LIST type: which predefined list item was selected
    list_value_selected = models.ForeignKey(LabTestListItem, null=True, blank=True, on_delete=models.PROTECT,
                                         help_text='Links to the selected list item.')

    # For TEXT type
    text_value = models.TextField(null=True, blank=True)

    # Common fields
    parameter_name_display = models.CharField(max_length=100, help_text='The name of the parameter being reported, e.g., Hemoglobin, Color, Microscopic Examination')
    is_abnormal = models.BooleanField(default=False, help_text='Automatically determined or manually set if abnormal.')
    value_notes = models.TextField(blank=True, help_text='Notes specific to this particular value/finding.')
    reported_at = models.DateTimeField(auto_now_add=True) # When this specific value was entered

    def get_value_display(self):
        if self.numeric_value is not None and self.numeric_range_item_tested:
            return f'{self.numeric_value} {self.numeric_range_item_tested.unit}'
        elif self.list_value_selected:
            return self.list_value_selected.item_value
        elif self.text_value:
            return self.text_value
        return 'N/A'

    def determine_abnormality(self):
        if self.numeric_value is not None and self.numeric_range_item_tested:
            lower = self.numeric_range_item_tested.lower_bound_normal
            upper = self.numeric_range_item_tested.upper_bound_normal
            if lower is not None and self.numeric_value < lower: return True
            if upper is not None and self.numeric_value > upper: return True
            return False
        elif self.list_value_selected:
            return not self.list_value_selected.is_normal_value
        # For text_value, abnormality is usually manually set or based on keywords (more complex)
        return self.is_abnormal # Default to manually set value

    def save(self, *args, **kwargs):
        if not self.pk: # Only on creation or if not manually set
            self.is_abnormal = self.determine_abnormality()

        # Populate parameter_name_display
        if not self.parameter_name_display:
            if self.numeric_range_item_tested:
                self.parameter_name_display = self.numeric_range_item_tested.parameter_name
            elif self.list_value_selected: # This might need manual setting if list items are generic
                self.parameter_name_display = self.lab_result.test_definition.name # Default to test name
            # For TEXT, parameter_name_display should usually be set manually.

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.parameter_name_display}: {self.get_value_display()}'
