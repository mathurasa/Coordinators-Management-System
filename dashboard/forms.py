from django import forms
from django.contrib.auth.models import User
from .models import Initiative, Task, Note, Document, UserProfile, District, InitiativeSheet, Event

class InitiativeForm(forms.ModelForm):
    class Meta:
        model = Initiative
        fields = ['title', 'description', 'initiative_type', 'status', 'district', 'start_date', 'end_date', 'budget', 'kpi_target']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'initiative_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'kpi_target': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'initiative', 'assigned_to', 'priority', 'status', 'due_date', 'progress_percentage']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'initiative': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'progress_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            if user.profile.role == 'admin':
                self.fields['assigned_to'].queryset = UserProfile.objects.filter(role='coordinator')
            else:
                self.fields['assigned_to'].queryset = UserProfile.objects.filter(
                    role='coordinator', 
                    district=user.profile.district
                )
                self.fields['initiative'].queryset = Initiative.objects.filter(district=user.profile.district)

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'note_type', 'initiative', 'task', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'initiative': forms.Select(attrs={'class': 'form-select'}),
            'task': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            if user.profile.role != 'admin':
                self.fields['initiative'].queryset = Initiative.objects.filter(district=user.profile.district)
                self.fields['task'].queryset = Task.objects.filter(initiative__district=user.profile.district)

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'initiative', 'task']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'initiative': forms.Select(attrs={'class': 'form-select'}),
            'task': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            if user.profile.role != 'admin':
                self.fields['initiative'].queryset = Initiative.objects.filter(district=user.profile.district)
                self.fields['task'].queryset = Task.objects.filter(initiative__district=user.profile.district)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'district', 'phone', 'bio', 'profile_picture']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Filter Forms
class InitiativeFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Initiative.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        required=False,
        empty_label="All Districts",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    initiative_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Initiative.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Task.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(Task.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        required=False,
        empty_label="All Districts",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class NoteFilterForm(forms.Form):
    note_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Note.NOTE_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        required=False,
        empty_label="All Districts",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class InitiativeSheetForm(forms.ModelForm):
    class Meta:
        model = InitiativeSheet
        fields = ['sheet_url']
        widgets = {
            'sheet_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://docs.google.com/spreadsheets/...'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_datetime', 'end_datetime', 'meet_link', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'meet_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/...'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
