from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import District, UserProfile, Initiative, Task, Note, Document

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_district')
    list_filter = ('profile__role', 'profile__district', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'N/A'
    get_role.short_description = 'Role'
    
    def get_district(self, obj):
        return obj.profile.district.name if hasattr(obj, 'profile') and obj.profile.district else 'N/A'
    get_district.short_description = 'District'

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'coordinator', 'initiative_type', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'initiative_type', 'district', 'coordinator')
    search_fields = ('title', 'description', 'district__name')
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'initiative', 'assigned_to', 'priority', 'status', 'due_date', 'progress_percentage', 'is_overdue')
    list_filter = ('status', 'priority', 'initiative__district', 'assigned_to')
    search_fields = ('title', 'description', 'initiative__title')
    date_hierarchy = 'due_date'
    ordering = ('-due_date', '-priority')
    
    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'

class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'initiative', 'author', 'note_type', 'created_at')
    list_filter = ('note_type', 'initiative__district', 'author', 'is_public')
    search_fields = ('title', 'content', 'initiative__title')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'initiative', 'uploaded_by', 'file_size', 'created_at')
    list_filter = ('initiative__district', 'uploaded_by')
    search_fields = ('title', 'description', 'initiative__title')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def file_size(self, obj):
        if obj.file_size:
            return f"{obj.file_size / 1024:.1f} KB"
        return "N/A"
    file_size.short_description = 'File Size'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register our models
admin.site.register(District, DistrictAdmin)
admin.site.register(Initiative, InitiativeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Document, DocumentAdmin)
