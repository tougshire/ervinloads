from django import forms
from django.forms import inlineformset_factory
from .models import Load, Location, Supplier

class LoadForm(forms.ModelForm):

    class Meta:
        model = Load
        fields = [
            'job_name',
            'po_number',
            'supplier',
            'spo_number',
            'description',
            'notes',
            'location',
            'status',
            'created_when',
            'updated_when',
            'do_install',
            'photo',
            'notification_groups',
            'completion',
        ]
        widgets = {
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'name',
        ]

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name',
        ]
