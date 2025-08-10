from django.urls import path
from . import views

urlpatterns = [
    # Dashboard - AdminLTE style URLs
    path('', views.dashboard_home, name='dashboard_home'),
    path('dashboard/', views.dashboard_home, name='dashboard'),
    path('dashboard/v1/', views.dashboard_home, name='dashboard_v1'),
    path('dashboard/v2/', views.dashboard_v2, name='dashboard_v2'),
    path('dashboard/v3/', views.dashboard_v3, name='dashboard_v3'),
    
    # Initiatives Management
    path('initiatives/', views.initiatives_list, name='initiatives_list'),
    path('initiatives/<int:pk>/', views.initiative_detail, name='initiative_detail'),
    path('initiatives/create/', views.InitiativeCreateView.as_view(), name='initiative_create'),
    path('initiatives/<int:pk>/edit/', views.InitiativeUpdateView.as_view(), name='initiative_update'),
    path('initiatives/<int:pk>/delete/', views.InitiativeDeleteView.as_view(), name='initiative_delete'),
    path('initiatives/<int:pk>/sheets/add/', views.InitiativeSheetCreateView.as_view(), name='initiative_sheet_add'),
    path('initiatives/<int:pk>/events/add/', views.EventCreateView.as_view(), name='initiative_event_add'),
    
    # Task Management
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    
    # Notes Management
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('notes/create/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    
    # Document Management
    path('documents/', views.documents_list, name='documents_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # Reports and Analytics
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/initiatives/', views.initiatives_report, name='initiatives_report'),
    path('reports/tasks/', views.tasks_report, name='tasks_report'),
    path('reports/export/', views.export_data, name='export_data'),
    
    # User Management (Admin only)
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/profile/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Districts Management
    path('districts/', views.districts_list, name='districts_list'),
    path('districts/create/', views.DistrictCreateView.as_view(), name='district_create'),
    path('districts/<int:pk>/', views.district_detail, name='district_detail'),
    path('districts/<int:pk>/edit/', views.DistrictUpdateView.as_view(), name='district_update'),
    path('districts/<int:pk>/delete/', views.DistrictDeleteView.as_view(), name='district_delete'),
    
    # Calendar and Timeline
    path('calendar/', views.calendar_view, name='calendar'),
    path('timeline/', views.timeline_view, name='timeline'),
    
    # Widgets and Components
    path('widgets/', views.widgets_page, name='widgets'),
    path('charts/', views.charts_page, name='charts'),
    
    # API endpoints
    path('api/dashboard-stats/', views.get_dashboard_stats, name='dashboard_stats'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/notifications/', views.get_notifications, name='notifications'),
    path('api/ai/summary/', views.ai_summary, name='ai_summary'),
    path('api/ai/suggestions/', views.ai_suggestions, name='ai_suggestions'),
]
