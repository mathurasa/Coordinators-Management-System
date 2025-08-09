from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from dashboard.models import District, UserProfile, Initiative, Task, Note

class Command(BaseCommand):
    help = 'Set up initial data for the Yarl IT Hub Coordinator Management System'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create superuser account',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up initial data for Yarl IT Hub Coordinator Management System...')
        )
        
        # Create superuser if requested
        if options['create_superuser']:
            self.create_superuser()
        
        # Create districts
        self.create_districts()
        
        # Create user profiles
        self.create_user_profiles()
        
        # Create sample initiatives
        self.create_sample_initiatives()
        
        # Create sample tasks
        self.create_sample_tasks()
        
        # Create sample notes
        self.create_sample_notes()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial data!')
        )
    
    def create_superuser(self):
        if not User.objects.filter(username='mathu').exists():
            superuser = User.objects.create_superuser(
                username='mathu',
                email='mathu@yarlithub.com',
                password='yit@2024',
                first_name='Mathu',
                last_name='Coordinator'
            )
            
            # Create admin profile
            UserProfile.objects.create(
                user=superuser,
                role='admin',
                phone='+94771234567',
                bio='Community Manager for Yarl IT Hub'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created superuser: {superuser.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists')
            )
    
    def create_districts(self):
        districts_data = [
            {
                'name': 'Batticaloa',
                'description': 'Eastern Province district focusing on rural development and education initiatives'
            },
            {
                'name': 'Ampara',
                'description': 'Agricultural and technology development programs in the Eastern Province'
            },
            {
                'name': 'Trincomalee',
                'description': 'Coastal development and fisheries technology programs'
            },
            {
                'name': 'Polonnaruwa',
                'description': 'Ancient city modernization and heritage preservation initiatives'
            },
            {
                'name': 'Anuradhapura',
                'description': 'Historical city development and archaeological technology projects'
            }
        ]
        
        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                name=district_data['name'],
                defaults={'description': district_data['description']}
            )
            if created:
                self.stdout.write(f'Created district: {district.name}')
            else:
                self.stdout.write(f'District already exists: {district.name}')
    
    def create_user_profiles(self):
        # Get districts
        districts = District.objects.all()
        
        # Create coordinators for each district
        coordinators_data = [
            {
                'username': 'coord_batticaloa',
                'email': 'batticaloa@yarlithub.com',
                'first_name': 'Priya',
                'last_name': 'Fernando',
                'district': 'Batticaloa',
                'phone': '+94771234001'
            },
            {
                'username': 'coord_ampara',
                'email': 'ampara@yarlithub.com',
                'first_name': 'Sunil',
                'last_name': 'Silva',
                'district': 'Ampara',
                'phone': '+94771234002'
            },
            {
                'username': 'coord_trincomalee',
                'email': 'trincomalee@yarlithub.com',
                'first_name': 'Kamani',
                'last_name': 'Perera',
                'district': 'Trincomalee',
                'phone': '+94771234003'
            },
            {
                'username': 'coord_polonnaruwa',
                'email': 'polonnaruwa@yarlithub.com',
                'first_name': 'Ravi',
                'last_name': 'Kumara',
                'district': 'Polonnaruwa',
                'phone': '+94771234004'
            },
            {
                'username': 'coord_anuradhapura',
                'email': 'anuradhapura@yarlithub.com',
                'first_name': 'Manjula',
                'last_name': 'Jayasinghe',
                'district': 'Anuradhapura',
                'phone': '+94771234005'
            }
        ]
        
        for coord_data in coordinators_data:
            if not User.objects.filter(username=coord_data['username']).exists():
                user = User.objects.create_user(
                    username=coord_data['username'],
                    email=coord_data['email'],
                    password='coord123',
                    first_name=coord_data['first_name'],
                    last_name=coord_data['last_name']
                )
                
                district = District.objects.get(name=coord_data['district'])
                UserProfile.objects.create(
                    user=user,
                    role='coordinator',
                    district=district,
                    phone=coord_data['phone'],
                    bio=f'District Coordinator for {district.name}'
                )
                
                self.stdout.write(f'Created coordinator: {user.username}')
            else:
                self.stdout.write(f'Coordinator already exists: {coord_data["username"]}')
    
    def create_sample_initiatives(self):
        # Get coordinators
        coordinators = UserProfile.objects.filter(role='coordinator')
        
        initiatives_data = [
            {
                'title': 'Digital Literacy Training Program',
                'description': 'Comprehensive digital literacy training for rural communities',
                'initiative_type': 'training',
                'status': 'active',
                'start_date': datetime.now().date(),
                'end_date': (datetime.now() + timedelta(days=90)).date(),
                'budget': 50000.00,
                'kpi_target': 'Train 200 participants, 80% completion rate'
            },
            {
                'title': 'Youth Leadership Workshop Series',
                'description': 'Leadership development workshops for young professionals',
                'initiative_type': 'workshop',
                'status': 'active',
                'start_date': (datetime.now() - timedelta(days=30)).date(),
                'end_date': (datetime.now() + timedelta(days=60)).date(),
                'budget': 30000.00,
                'kpi_target': '5 workshops, 150 participants total'
            },
            {
                'title': 'Community Tech Mentorship',
                'description': 'One-on-one mentorship program for technology enthusiasts',
                'initiative_type': 'mentorship',
                'status': 'active',
                'start_date': datetime.now().date(),
                'end_date': (datetime.now() + timedelta(days=180)).date(),
                'budget': 25000.00,
                'kpi_target': '50 mentor-mentee pairs, 6-month program'
            }
        ]
        
        for i, coord in enumerate(coordinators[:3]):
            if i < len(initiatives_data):
                init_data = initiatives_data[i]
                initiative, created = Initiative.objects.get_or_create(
                    title=init_data['title'],
                    defaults={
                        'description': init_data['description'],
                        'initiative_type': init_data['initiative_type'],
                        'status': init_data['status'],
                        'district': coord.district,
                        'coordinator': coord,
                        'start_date': init_data['start_date'],
                        'end_date': init_data['end_date'],
                        'budget': init_data['budget'],
                        'kpi_target': init_data['kpi_target']
                    }
                )
                if created:
                    self.stdout.write(f'Created initiative: {initiative.title}')
    
    def create_sample_tasks(self):
        initiatives = Initiative.objects.all()
        coordinators = UserProfile.objects.filter(role='coordinator')
        
        for initiative in initiatives:
            # Create 2-3 tasks per initiative
            tasks_data = [
                {
                    'title': f'Venue Booking for {initiative.title}',
                    'description': 'Book appropriate venues for the program activities',
                    'priority': 'high',
                    'status': 'completed',
                    'due_date': timezone.now() + timedelta(days=7),
                    'progress_percentage': 100
                },
                {
                    'title': f'Participant Registration for {initiative.title}',
                    'description': 'Set up registration system and collect participant details',
                    'priority': 'medium',
                    'status': 'in_progress',
                    'due_date': timezone.now() + timedelta(days=14),
                    'progress_percentage': 60
                },
                {
                    'title': f'Material Preparation for {initiative.title}',
                    'description': 'Prepare training materials and resources',
                    'priority': 'medium',
                    'status': 'not_started',
                    'due_date': timezone.now() + timedelta(days=21),
                    'progress_percentage': 0
                }
            ]
            
            for task_data in tasks_data:
                task, created = Task.objects.get_or_create(
                    title=task_data['title'],
                    defaults={
                        'description': task_data['description'],
                        'initiative': initiative,
                        'assigned_to': initiative.coordinator,
                        'created_by': initiative.coordinator,
                        'priority': task_data['priority'],
                        'status': task_data['status'],
                        'due_date': task_data['due_date'],
                        'progress_percentage': task_data['progress_percentage']
                    }
                )
                if created:
                    self.stdout.write(f'Created task: {task.title}')
    
    def create_sample_notes(self):
        initiatives = Initiative.objects.all()
        
        for initiative in initiatives:
            notes_data = [
                {
                    'title': f'Planning Meeting - {initiative.title}',
                    'content': 'Initial planning meeting held to discuss objectives, timeline, and resource requirements. Key stakeholders identified and roles assigned.',
                    'note_type': 'meeting',
                    'is_public': True
                },
                {
                    'title': f'Progress Update - {initiative.title}',
                    'content': 'Weekly progress update: Registration process initiated, venue confirmations pending, material development on track.',
                    'note_type': 'milestone',
                    'is_public': True
                }
            ]
            
            for note_data in notes_data:
                note, created = Note.objects.get_or_create(
                    title=note_data['title'],
                    defaults={
                        'content': note_data['content'],
                        'note_type': note_data['note_type'],
                        'initiative': initiative,
                        'author': initiative.coordinator,
                        'is_public': note_data['is_public']
                    }
                )
                if created:
                    self.stdout.write(f'Created note: {note.title}')
