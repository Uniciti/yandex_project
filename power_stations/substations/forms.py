# substations/forms.py
from django import forms
from .models import Substation, MaintenanceRecord, SubstationGroup, SubstationType, MaintenanceStatus

class SubstationForm(forms.ModelForm):
    last_maintenance = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        ),
        label="Дата последнего обслуживания",
    )
    
    next_maintenance = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        ),
        label="Дата следующего обслуживания",
    )

    class Meta:
        model = Substation
        fields = [
            'name', 'power', 'voltage', 'city', 'group', 
            'substation_type', 'image', 'address', 'notes', 
            'is_active', 'last_maintenance', 'next_maintenance'
        ]

    def clean(self):
        cleaned_data = super().clean()
        last_maintenance = cleaned_data.get('last_maintenance')
        next_maintenance = cleaned_data.get('next_maintenance')

        if last_maintenance and next_maintenance and last_maintenance > next_maintenance:
            raise forms.ValidationError(
                "Дата следующего обслуживания должна быть позже даты последнего обслуживания"
            )

        return cleaned_data

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['status', 'scheduled_date', 'completed_date', 'description']
        widgets = {
            'scheduled_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}
            ),
            'completed_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_date'].required = True
        self.fields['description'].required = True

class SubstationGroupForm(forms.ModelForm):
    class Meta:
        model = SubstationGroup
        fields = ['name', 'description', 'responsible_person', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'responsible_person': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'contact_info': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
        }

class SubstationTypeForm(forms.ModelForm):
    class Meta:
        model = SubstationType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
        }

class MaintenanceStatusForm(forms.ModelForm):
    class Meta:
        model = MaintenanceStatus
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
        }