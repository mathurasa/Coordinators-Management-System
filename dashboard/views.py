from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from .models import District, UserProfile, Initiative, Task, Note, Document, InitiativeSheet, Event
from .forms import InitiativeForm, TaskForm, NoteForm, DocumentForm, UserProfileForm, InitiativeSheetForm, EventForm, EventAdminForm
from datetime import datetime, timedelta
import csv
import json

def is_admin(user):
    """Check if user is admin"""
    return hasattr(user, 'profile') and user.profile.role == 'admin'

def is_coordinator(user):
    """Check if user is coordinator"""
    return hasattr(user, 'profile') and user.profile.role == 'coordinator'

# Custom login view to handle CSRF properly
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'dashboard/custom_login.html')

@login_required
def dashboard_home(request):
    """Main dashboard view"""
    user_profile = request.user.profile
    
    # Get data based on user role
    if user_profile.role == 'admin':
        # Admin sees all data
        initiatives = Initiative.objects.all()
        tasks = Task.objects.all()
        districts_qs = District.objects.all()
        coordinators = UserProfile.objects.filter(role='coordinator')
    else:
        # Coordinator sees only their district data
        initiatives = Initiative.objects.filter(district=user_profile.district)
        tasks = Task.objects.filter(initiative__district=user_profile.district)
        districts_qs = (
            District.objects.filter(pk=user_profile.district.pk)
            if user_profile.district
            else District.objects.none()
        )
        coordinators = UserProfile.objects.filter(district=user_profile.district, role='coordinator')
    
    # Calculate statistics
    total_initiatives = initiatives.count()
    active_initiatives = initiatives.filter(status='active').count()
    completed_initiatives = initiatives.filter(status='completed').count()
    
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    overdue_tasks = tasks.filter(due_date__lt=timezone.now(), status__in=['not_started', 'in_progress']).count()
    
    # Recent activities
    recent_tasks = tasks.order_by('-created_at')[:5]
    recent_notes = Note.objects.filter(initiative__in=initiatives).order_by('-created_at')[:5]
    
    # Weekly progress
    week_ago = timezone.now() - timedelta(days=7)
    weekly_completed_tasks = tasks.filter(completed_at__gte=week_ago).count()
    
    # Annotate districts for template counters
    districts = districts_qs.annotate(
        total_initiatives=Count('initiatives', distinct=True),
        active_initiatives=Count('initiatives', filter=Q(initiatives__status='active'), distinct=True),
    )

    context = {
        'user_profile': user_profile,
        'total_initiatives': total_initiatives,
        'active_initiatives': active_initiatives,
        'completed_initiatives': completed_initiatives,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'weekly_completed_tasks': weekly_completed_tasks,
        'recent_tasks': recent_tasks,
        'recent_notes': recent_notes,
        'districts': districts,
        'coordinators': coordinators,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def initiatives_list(request):
    """List all initiatives"""
    user_profile = request.user.profile

    queryset = Initiative.objects.all() if user_profile.role == 'admin' else Initiative.objects.filter(
        district=user_profile.district
    )

    # Filtering
    status_filter = request.GET.get('status')
    district_filter = request.GET.get('district')
    type_filter = request.GET.get('type')
    search_query = request.GET.get('search')

    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if district_filter:
        queryset = queryset.filter(district__name=district_filter)
    if type_filter:
        queryset = queryset.filter(initiative_type=type_filter)
    if search_query:
        queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    # Optimize and annotate for template counters
    initiatives = queryset.select_related('district', 'coordinator__user').annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='completed')),
        notes_count=Count('notes'),
    )

    # District options for admin filtering
    districts = District.objects.all() if user_profile.role == 'admin' else District.objects.filter(
        pk=user_profile.district.pk
    ) if user_profile.district else District.objects.none()

    context = {
        'initiatives': initiatives,
        'user_profile': user_profile,
        'status_choices': Initiative.STATUS_CHOICES,
        'type_choices': Initiative.TYPE_CHOICES,
        'districts': districts,
    }

    return render(request, 'dashboard/initiatives_list.html', context)

@login_required
def initiative_detail(request, pk):
    """Detail view for an initiative including sheets and events"""
    user_profile = request.user.profile
    if user_profile.role == 'admin':
        initiative = get_object_or_404(Initiative, pk=pk)
    else:
        initiative = get_object_or_404(Initiative, pk=pk, district=user_profile.district)

    tasks = initiative.tasks.all().select_related('assigned_to')
    notes = initiative.notes.all()
    documents = initiative.documents.all()
    sheets = initiative.sheets.select_related('coordinator').all()
    events = initiative.events.filter(start_datetime__gte=timezone.now()-timedelta(days=30)).order_by('start_datetime')

    # Derive progress as average of task progress if tasks exist
    if tasks.exists():
        total_progress = sum(t.progress_percentage for t in tasks)
        progress = int(total_progress / tasks.count())
    else:
        progress = 0

    context = {
        'initiative': initiative,
        'tasks': tasks,
        'notes': notes,
        'documents': documents,
        'sheets': sheets,
        'events': events,
        'progress': progress,
        'sheet_form': InitiativeSheetForm(),
        'event_form': EventForm(),
    }
    return render(request, 'dashboard/initiative_detail.html', context)

@login_required
def tasks_list(request):
    """List all tasks"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(initiative__district=user_profile.district)
    
    # Filtering
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    district_filter = request.GET.get('district')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if district_filter:
        tasks = tasks.filter(initiative__district__name=district_filter)
    
    context = {
        'tasks': tasks,
        'user_profile': user_profile,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    
    return render(request, 'dashboard/tasks_list.html', context)

@login_required
def task_detail(request, pk):
    """Detail view for a task"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, initiative__district=user_profile.district)
    
    notes = task.notes.all()
    documents = task.documents.all()
    
    context = {
        'task': task,
        'notes': notes,
        'documents': documents,
        'user_profile': user_profile,
    }
    
    return render(request, 'dashboard/task_detail.html', context)

@login_required
def notes_list(request):
    """List all notes"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        notes = Note.objects.all()
    else:
        notes = Note.objects.filter(initiative__district=user_profile.district)
    
    # Filtering
    type_filter = request.GET.get('type')
    district_filter = request.GET.get('district')
    
    if type_filter:
        notes = notes.filter(note_type=type_filter)
    if district_filter:
        notes = notes.filter(initiative__district__name=district_filter)
    
    context = {
        'notes': notes,
        'user_profile': user_profile,
        'type_choices': Note.NOTE_TYPE_CHOICES,
    }
    
    return render(request, 'dashboard/notes_list.html', context)

@login_required
def documents_list(request):
    """List all documents"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(initiative__district=user_profile.district)
    
    # Filtering
    district_filter = request.GET.get('district')
    
    if district_filter:
        documents = documents.filter(initiative__district__name=district_filter)
    
    context = {
        'documents': documents,
        'user_profile': user_profile,
    }
    
    return render(request, 'dashboard/documents_list.html', context)

# Form Views
class InitiativeCreateView(LoginRequiredMixin, CreateView):
    model = Initiative
    form_class = InitiativeForm
    template_name = 'dashboard/initiative_form.html'
    success_url = reverse_lazy('initiatives_list')
    
    def form_valid(self, form):
        form.instance.coordinator = self.request.user.profile
        messages.success(self.request, 'Initiative created successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user if the form supports user-scoped querysets
        kwargs.setdefault('user', self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # No object yet on create; provide zeroed stats for template
        context.setdefault('total_tasks_count', 0)
        context.setdefault('completed_tasks_count', 0)
        context.setdefault('notes_count', 0)
        context.setdefault('documents_count', 0)
        return context

class InitiativeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Initiative
    form_class = InitiativeForm
    template_name = 'dashboard/initiative_form.html'
    success_url = reverse_lazy('initiatives_list')
    
    def test_func(self):
        initiative = self.get_object()
        user_profile = self.request.user.profile
        return user_profile.role == 'admin' or initiative.coordinator == user_profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Initiative updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initiative = self.object
        context['total_tasks_count'] = initiative.tasks.count()
        context['completed_tasks_count'] = initiative.tasks.filter(status='completed').count()
        context['notes_count'] = initiative.notes.count()
        context['documents_count'] = initiative.documents.count()
        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'dashboard/task_form.html'
    success_url = reverse_lazy('tasks_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user.profile
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'dashboard/task_form.html'
    success_url = reverse_lazy('tasks_list')
    
    def test_func(self):
        task = self.get_object()
        user_profile = self.request.user.profile
        return user_profile.role == 'admin' or task.assigned_to == user_profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('notes_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        messages.success(self.request, 'Note created successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('notes_list')
    
    def test_func(self):
        note = self.get_object()
        user_profile = self.request.user.profile
        return user_profile.role == 'admin' or note.author == user_profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Note updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'dashboard/document_form.html'
    success_url = reverse_lazy('documents_list')
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user.profile
        messages.success(self.request, 'Document uploaded successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

class InitiativeSheetCreateView(LoginRequiredMixin, CreateView):
    model = InitiativeSheet
    form_class = InitiativeSheetForm
    template_name = 'dashboard/initiative_sheet_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.initiative = get_object_or_404(Initiative, pk=kwargs['pk'])
        # permission check
        if request.user.profile.role != 'admin' and request.user.profile.district != self.initiative.district:
            messages.error(request, 'Access denied.')
            return redirect('dashboard_home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.initiative = self.initiative
        form.instance.coordinator = self.request.user.profile if self.request.user.profile.role == 'coordinator' else self.initiative.coordinator
        messages.success(self.request, 'Sheet link added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('initiative_detail', args=[self.initiative.pk])

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.initiative = get_object_or_404(Initiative, pk=kwargs['pk'])
        if request.user.profile.role != 'admin' and request.user.profile.district != self.initiative.district:
            messages.error(request, 'Access denied.')
            return redirect('dashboard_home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.initiative = self.initiative
        form.instance.organizer = self.request.user.profile
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('initiative_detail', args=[self.initiative.pk])

# API Views for AJAX
@login_required
def update_task_status(request, pk):
    """Update task status via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get('status')
        progress = request.POST.get('progress', 0)
        
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.progress_percentage = int(progress)
            
            if new_status == 'completed':
                task.completed_at = timezone.now()
            
            task.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def get_dashboard_stats(request):
    """Get dashboard statistics via AJAX"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        initiatives = Initiative.objects.all()
        tasks = Task.objects.all()
    else:
        initiatives = Initiative.objects.filter(district=user_profile.district)
        tasks = Task.objects.filter(initiative__district=user_profile.district)
    
    stats = {
        'total_initiatives': initiatives.count(),
        'active_initiatives': initiatives.filter(status='active').count(),
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'overdue_tasks': tasks.filter(due_date__lt=timezone.now(), status__in=['not_started', 'in_progress']).count(),
    }
    
    return JsonResponse(stats)

# Additional Dashboard Views (AdminLTE Style)
@login_required
def dashboard_v2(request):
    """Alternative dashboard view v2"""
    return render(request, 'dashboard/dashboard_v2.html', {
        'user_profile': request.user.profile,
    })

@login_required
def dashboard_v3(request):
    """Alternative dashboard view v3"""
    return render(request, 'dashboard/dashboard_v3.html', {
        'user_profile': request.user.profile,
    })

# Detail Views
@login_required
def note_detail(request, pk):
    """Detail view for a note"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        note = get_object_or_404(Note, pk=pk)
    else:
        note = get_object_or_404(Note, pk=pk, initiative__district=user_profile.district)
    
    return render(request, 'dashboard/note_detail.html', {
        'note': note,
        'user_profile': user_profile,
    })

@login_required
def document_detail(request, pk):
    """Detail view for a document"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        document = get_object_or_404(Document, pk=pk)
    else:
        document = get_object_or_404(Document, pk=pk, initiative__district=user_profile.district)
    
    return render(request, 'dashboard/document_detail.html', {
        'document': document,
        'user_profile': user_profile,
    })

# Delete Views
class InitiativeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Initiative
    template_name = 'dashboard/initiative_confirm_delete.html'
    success_url = reverse_lazy('initiatives_list')
    
    def test_func(self):
        initiative = self.get_object()
        return self.request.user.profile.role == 'admin' or initiative.coordinator == self.request.user.profile

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'dashboard/task_confirm_delete.html'
    success_url = reverse_lazy('tasks_list')
    
    def test_func(self):
        task = self.get_object()
        return self.request.user.profile.role == 'admin' or task.assigned_to == self.request.user.profile

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = 'dashboard/note_confirm_delete.html'
    success_url = reverse_lazy('notes_list')
    
    def test_func(self):
        note = self.get_object()
        return self.request.user.profile.role == 'admin' or note.author == self.request.user.profile

class DocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Document
    template_name = 'dashboard/document_confirm_delete.html'
    success_url = reverse_lazy('documents_list')
    
    def test_func(self):
        document = self.get_object()
        return self.request.user.profile.role == 'admin' or document.uploaded_by == self.request.user.profile

# Reports and Analytics
@login_required
def reports_dashboard(request):
    """Reports and analytics dashboard"""
    user_profile = request.user.profile
    
    context = {
        'user_profile': user_profile,
    }
    
    return render(request, 'dashboard/reports_dashboard.html', context)

@login_required
def initiatives_report(request):
    """Initiatives report"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        initiatives = Initiative.objects.all()
    else:
        initiatives = Initiative.objects.filter(district=user_profile.district)
    
    context = {
        'initiatives': initiatives,
        'user_profile': user_profile,
    }
    
    return render(request, 'dashboard/initiatives_report.html', context)

@login_required
def tasks_report(request):
    """Tasks report"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(initiative__district=user_profile.district)
    
    context = {
        'tasks': tasks,
        'user_profile': user_profile,
    }
    
    return render(request, 'dashboard/tasks_report.html', context)

@login_required
def export_data(request):
    """Export data to CSV"""
    export_type = request.GET.get('type', 'initiatives')
    user_profile = request.user.profile
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'initiatives':
        response['Content-Disposition'] = 'attachment; filename="initiatives.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'District', 'Coordinator', 'Type', 'Status', 'Start Date', 'End Date'])
        
        if user_profile.role == 'admin':
            initiatives = Initiative.objects.all()
        else:
            initiatives = Initiative.objects.filter(district=user_profile.district)
        
        for initiative in initiatives:
            writer.writerow([
                initiative.title,
                initiative.district.name,
                initiative.coordinator.user.get_full_name(),
                initiative.get_initiative_type_display(),
                initiative.get_status_display(),
                initiative.start_date,
                initiative.end_date or '',
            ])
    elif export_type == 'tasks':
        response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Initiative', 'Assigned To', 'Priority', 'Status', 'Due Date', 'Progress %'])
        if user_profile.role == 'admin':
            tasks = Task.objects.select_related('initiative', 'assigned_to__user')
        else:
            tasks = Task.objects.filter(initiative__district=user_profile.district).select_related('initiative', 'assigned_to__user')
        for task in tasks:
            writer.writerow([
                task.title,
                task.initiative.title,
                task.assigned_to.user.get_full_name(),
                task.get_priority_display(),
                task.get_status_display(),
                task.due_date,
                task.progress_percentage,
            ])
    
    return response

# User Management (Admin Only)
@login_required
def users_list(request):
    """List all users (admin only)"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard_home')
    
    users = User.objects.all().select_related('profile')
    
    context = {
        'users': users,
        'user_profile': request.user.profile,
    }
    
    return render(request, 'dashboard/users_list.html', context)

@login_required
def user_detail(request, pk):
    """User detail view (admin only)"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard_home')
    
    user = get_object_or_404(User, pk=pk)
    
    context = {
        'profile_user': user,
        'user_profile': request.user.profile,
    }
    
    return render(request, 'dashboard/user_detail.html', context)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', 'is_active']
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('users_list')
    
    def test_func(self):
        return self.request.user.profile.role == 'admin'

class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'dashboard/user_profile_form.html'
    success_url = reverse_lazy('users_list')

    def test_func(self):
        return self.request.user.profile.role == 'admin'

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dashboard/user_create.html'

    def test_func(self):
        return self.request.user.profile.role == 'admin'

    def get(self, request):
        return render(request, self.template_name, {
            'user_form': UserCreationForm(),
            'profile_form': UserProfileForm(),
        })

    def post(self, request):
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Set additional fields
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.is_active = True
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'User created successfully!')
            return redirect('users_list')
        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'dashboard/user_confirm_delete.html'
    success_url = reverse_lazy('users_list')

    def test_func(self):
        # Admins cannot delete themselves
        return self.request.user.profile.role == 'admin' and self.get_object() != self.request.user

# Districts Management
@login_required
def districts_list(request):
    """List all districts"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard_home')

    districts = District.objects.all()
    
    context = {
        'districts': districts,
        'user_profile': request.user.profile,
    }
    
    return render(request, 'dashboard/districts_list.html', context)

@login_required
def district_detail(request, pk):
    """District detail view"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard_home')
    district = get_object_or_404(District, pk=pk)
    
    context = {
        'district': district,
        'user_profile': request.user.profile,
    }
    
    return render(request, 'dashboard/district_detail.html', context)

class DistrictCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = District
    fields = ['name', 'description']
    template_name = 'dashboard/district_form.html'
    success_url = reverse_lazy('districts_list')

    def test_func(self):
        return self.request.user.profile.role == 'admin'

class DistrictUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = District
    fields = ['name', 'description']
    template_name = 'dashboard/district_form.html'
    success_url = reverse_lazy('districts_list')

    def test_func(self):
        return self.request.user.profile.role == 'admin'

class DistrictDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = District
    template_name = 'dashboard/district_confirm_delete.html'
    success_url = reverse_lazy('districts_list')

    def test_func(self):
        return self.request.user.profile.role == 'admin'

# Calendar and Timeline
@login_required
def calendar_view(request):
    """Calendar view"""
    user_profile = request.user.profile
    # Gather upcoming events limits
    if user_profile.role == 'admin':
        events = Event.objects.select_related('initiative').order_by('start_datetime')[:50]
        form = EventAdminForm(user=request.user)
    else:
        events = Event.objects.filter(initiative__district=user_profile.district).select_related('initiative').order_by('start_datetime')[:50]
        form = EventAdminForm(user=request.user)

    return render(request, 'dashboard/calendar.html', {
        'user_profile': user_profile,
        'events': events,
        'event_form': form,
    })

@login_required
def timeline_view(request):
    """Timeline view"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        activities = Task.objects.all().order_by('-created_at')[:20]
    else:
        activities = Task.objects.filter(initiative__district=user_profile.district).order_by('-created_at')[:20]
    
    context = {
        'activities': activities,
        'user_profile': user_profile,
    }
    
    return render(request, 'dashboard/timeline.html', context)

# Widgets and Components
@login_required
def widgets_page(request):
    """Widgets showcase page"""
    context = {
        'user_profile': request.user.profile,
    }
    
    return render(request, 'dashboard/widgets.html', context)

@login_required
def charts_page(request):
    """Charts showcase page"""
    context = {
        'user_profile': request.user.profile,
    }
    
    return render(request, 'dashboard/charts.html', context)

# API Views
@login_required
def get_chart_data(request):
    """Get chart data for dashboard"""
    user_profile = request.user.profile
    
    if user_profile.role == 'admin':
        initiatives = Initiative.objects.all()
        tasks = Task.objects.all()
    else:
        initiatives = Initiative.objects.filter(district=user_profile.district)
        tasks = Task.objects.filter(initiative__district=user_profile.district)
    
    # Monthly data for the last 6 months
    months = []
    initiative_data = []
    task_data = []
    
    for i in range(6, 0, -1):
        month_date = timezone.now() - timedelta(days=30 * i)
        months.append(month_date.strftime('%b'))
        
        month_initiatives = initiatives.filter(created_at__year=month_date.year, created_at__month=month_date.month)
        month_tasks = tasks.filter(created_at__year=month_date.year, created_at__month=month_date.month)
        
        initiative_data.append(month_initiatives.count())
        task_data.append(month_tasks.count())
    
    chart_data = {
        'labels': months,
        'datasets': [
            {
                'label': 'Initiatives',
                'data': initiative_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2
            },
            {
                'label': 'Tasks',
                'data': task_data,
                'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 2
            }
        ]
    }
    
    return JsonResponse(chart_data)

@login_required
def get_notifications(request):
    """Get notifications for user"""
    user_profile = request.user.profile
    
    # Get overdue tasks
    if user_profile.role == 'admin':
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['not_started', 'in_progress']
        ).order_by('-due_date')[:5]
    else:
        overdue_tasks = Task.objects.filter(
            initiative__district=user_profile.district,
            due_date__lt=timezone.now(),
            status__in=['not_started', 'in_progress']
        ).order_by('-due_date')[:5]
    
    notifications = []
    for task in overdue_tasks:
        notifications.append({
            'type': 'warning',
            'message': f'Task "{task.title}" is overdue',
            'url': f'/tasks/{task.pk}/',
            'time': task.due_date.strftime('%Y-%m-%d')
        })
    
    return JsonResponse({'notifications': notifications})

# AI assistant stubs
@login_required
def ai_summary(request):
    """Return AI-like daily/weekly summaries based on recent data (stub)."""
    user_profile = request.user.profile
    if user_profile.role == 'admin':
        tasks = Task.objects.all()
        notes = Note.objects.all()
    else:
        tasks = Task.objects.filter(initiative__district=user_profile.district)
        notes = Note.objects.filter(initiative__district=user_profile.district)

    week_ago = timezone.now() - timedelta(days=7)
    completed_week = tasks.filter(completed_at__gte=week_ago).count()
    created_week = tasks.filter(created_at__gte=week_ago).count()
    notes_week = notes.filter(created_at__gte=week_ago).count()

    summary = {
        'daily': f"{tasks.filter(updated_at__date=timezone.now().date()).count()} tasks updated today.",
        'weekly': f"{completed_week} tasks completed and {created_week} new tasks created in the last 7 days. {notes_week} notes added.",
        'recommendations': [
            'Prioritize overdue high-urgency tasks in the next 48 hours.',
            'Schedule a review meeting for initiatives with < 30% progress.',
            'Encourage coordinators to add weekly notes for better visibility.'
        ]
    }
    return JsonResponse(summary)

@login_required
def ai_suggestions(request):
    """Provide simple, rule-based next-step suggestions (stub)."""
    user_profile = request.user.profile
    queryset = Task.objects.all() if user_profile.role == 'admin' else Task.objects.filter(initiative__district=user_profile.district)
    overdue = list(queryset.filter(due_date__lt=timezone.now(), status__in=['not_started', 'in_progress']).values('title')[:5])
    low_progress_inits = []
    for init in (Initiative.objects.all() if user_profile.role == 'admin' else Initiative.objects.filter(district=user_profile.district)):
        tasks = init.tasks.all()
        if tasks.exists():
            avg = sum(t.progress_percentage for t in tasks) / tasks.count()
            if avg < 30:
                low_progress_inits.append(init.title)
    return JsonResponse({
        'overdue_tasks': overdue,
        'low_progress_initiatives': low_progress_inits[:5],
        'ideas': [
            'Host a cross-district knowledge sharing session.',
            'Leverage alumni mentors for YGC cohorts.',
            'Pilot a mini-hackathon under Makerspace.'
        ]
    })
