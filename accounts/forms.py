from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Patient

class PatientCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Patient
        fields = ('username', 'email') # Add other fields as they are added to Patient model

class PatientChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Patient
        fields = ('username', 'email') # Add other fields
