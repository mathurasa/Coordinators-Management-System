from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator

class District(models.Model):
    """Model for representing districts"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Extended user profile with role and district assignment"""
    ROLE_CHOICES = [
        ('admin', 'Community Manager'),
        ('coordinator', 'District Coordinator'),
        ('readonly', 'Read Only'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='coordinator')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

class Initiative(models.Model):
    """Model for representing initiatives"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('training', 'Training Program'),
        ('workshop', 'Workshop'),
        ('mentorship', 'Mentorship'),
        ('community', 'Community Outreach'),
        ('research', 'Research Project'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    initiative_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='initiatives')
    coordinator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='managed_initiatives')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    kpi_target = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.district.name}"

class Task(models.Model):
    """Model for representing tasks"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='created_tasks')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date', '-priority']
    
    def __str__(self):
        return f"{self.title} - {self.initiative.title}"
    
    def is_overdue(self):
        return self.due_date < timezone.now() and self.status != 'completed'

class Note(models.Model):
    """Model for representing notes and comments"""
    NOTE_TYPE_CHOICES = [
        ('meeting', 'Meeting Notes'),
        ('workshop', 'Workshop Summary'),
        ('general', 'General Note'),
        ('milestone', 'Milestone Update'),
        ('feedback', 'Feedback'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, default='general')
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='notes')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_notes')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.initiative.title}"

class Document(models.Model):
    """Model for file uploads"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'])]
    )
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='documents')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    uploaded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='uploaded_documents')
    file_size = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.initiative.title}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
