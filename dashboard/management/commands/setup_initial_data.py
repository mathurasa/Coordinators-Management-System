from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from dashboard.models import District, UserProfile, Initiative, Task, Note, InitiativeSheet, Event

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
        
        # Create preloaded initiatives
        self.create_preloaded_initiatives()
        
        # Create sample tasks
        self.create_sample_tasks()
        
        # Create sample notes
        self.create_sample_notes()

        # Create sample sheets and events
        self.create_sample_sheets_and_events()
        
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
            {'name': 'Batticaloa', 'description': 'Eastern Province district focusing on rural development and education initiatives'},
            {'name': 'Ampara', 'description': 'Agricultural and technology development programs in the Eastern Province'},
            {'name': 'Trincomalee', 'description': 'Coastal development and fisheries technology programs'},
            {'name': 'Polonnaruwa', 'description': 'Ancient city modernization and heritage preservation initiatives'},
            {'name': 'Anuradhapura', 'description': 'Historical city development and archaeological technology projects'},
        ]
        for data in districts_data:
            District.objects.get_or_create(name=data['name'], defaults={'description': data['description']})
    
    def create_user_profiles(self):
        coordinators_data = [
            {'username': 'coord_batticaloa', 'email': 'batticaloa@yarlithub.com', 'first_name': 'Priya', 'last_name': 'Fernando', 'district': 'Batticaloa', 'phone': '+94771234001'},
            {'username': 'coord_ampara', 'email': 'ampara@yarlithub.com', 'first_name': 'Sunil', 'last_name': 'Silva', 'district': 'Ampara', 'phone': '+94771234002'},
            {'username': 'coord_trincomalee', 'email': 'trincomalee@yarlithub.com', 'first_name': 'Kamani', 'last_name': 'Perera', 'district': 'Trincomalee', 'phone': '+94771234003'},
            {'username': 'coord_polonnaruwa', 'email': 'polonnaruwa@yarlithub.com', 'first_name': 'Ravi', 'last_name': 'Kumara', 'district': 'Polonnaruwa', 'phone': '+94771234004'},
            {'username': 'coord_anuradhapura', 'email': 'anuradhapura@yarlithub.com', 'first_name': 'Manjula', 'last_name': 'Jayasinghe', 'district': 'Anuradhapura', 'phone': '+94771234005'},
        ]
        for data in coordinators_data:
            if not User.objects.filter(username=data['username']).exists():
                user = User.objects.create_user(
                    username=data['username'], email=data['email'], password='coord123',
                    first_name=data['first_name'], last_name=data['last_name']
                )
                district = District.objects.get(name=data['district'])
                UserProfile.objects.create(user=user, role='coordinator', district=district, phone=data['phone'], bio=f'District Coordinator for {district.name}')
    
    def create_preloaded_initiatives(self):
        titles = [
            'Makerspace',
            'Puthiyapayanangal',
            'YGC-Junior',
            'YGC-Senior',
            'Accelerator Program',
            'WEHub',
            'Uki',
        ]
        # Assign to first few coordinators round-robin
        coordinators = list(UserProfile.objects.filter(role='coordinator'))
        if not coordinators:
            return
        start = datetime.now().date()
        for i, title in enumerate(titles):
            coord = coordinators[i % len(coordinators)]
            Initiative.objects.get_or_create(
                title=title,
                district=coord.district,
                defaults={
                    'description': f'{title} initiative description',
                    'initiative_type': 'other',
                    'status': 'active',
                    'coordinator': coord,
                    'start_date': start,
                    'end_date': start + timedelta(days=120),
                    'budget': 100000.00,
                    'kpi_target': 'Define KPIs for this initiative'
                }
            )
    
    def create_sample_tasks(self):
        initiatives = Initiative.objects.all()
        for initiative in initiatives:
            Task.objects.get_or_create(
                title=f'Kickoff meeting for {initiative.title}',
                initiative=initiative,
                defaults={
                    'description': 'Plan agenda and stakeholders',
                    'assigned_to': initiative.coordinator,
                    'created_by': initiative.coordinator,
                    'priority': 'high',
                    'status': 'in_progress',
                    'due_date': timezone.now() + timedelta(days=7),
                    'progress_percentage': 25
                }
            )

    def create_sample_notes(self):
        for initiative in Initiative.objects.all():
            Note.objects.get_or_create(
                title=f'Initial planning - {initiative.title}',
                initiative=initiative,
                defaults={
                    'content': 'Draft objectives and milestones.',
                    'note_type': 'meeting',
                    'author': initiative.coordinator,
                    'is_public': True,
                }
            )

    def create_sample_sheets_and_events(self):
        for initiative in Initiative.objects.all():
            # Create a sample sheet link per initiative/coordinator
            InitiativeSheet.objects.get_or_create(
                initiative=initiative,
                coordinator=initiative.coordinator,
                defaults={'sheet_url': 'https://docs.google.com/spreadsheets/d/EXAMPLE'}
            )
            # Create a sample event with meet link
            Event.objects.get_or_create(
                initiative=initiative,
                title=f'{initiative.title} Review Meeting',
                start_datetime=timezone.now() + timedelta(days=3),
                end_datetime=timezone.now() + timedelta(days=3, hours=2),
                organizer=initiative.coordinator,
                defaults={
                    'description': 'Monthly review and planning',
                    'meet_link': 'https://meet.google.com/xyz-abcd-123',
                    'location': 'Online'
                }
            )
