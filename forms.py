from django import forms
from django.forms import inlineformset_factory
from .models import Load, Location, Notification, Supplier

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

class LocationMergeForm(forms.Form):
    def __init__(self, **kwargs):
        init = super().__init__(**kwargs)
        print('tp 2253e59', self.initial)
        return init

    merge_from=forms.ModelChoiceField(Location.objects.all())
    merge_to=forms.ModelChoiceField(Location.objects.all())

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            'load',
            'created_when',
        ]
class NotificationSendForm(forms.Form):

    notifications = forms.ModelMultipleChoiceField(
        queryset = Notification.objects.all(),
        widget = forms.CheckboxSelectMultiple
    )
    operation = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices = [('ss', 'Send Selected then Delete Selected'), ('sa', 'Send Selected then Delete All'), ('ns', 'Delete Selected, Don\'t Send')],
        initial = 'ss'
    )

