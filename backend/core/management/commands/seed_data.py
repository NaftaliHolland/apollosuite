from datetime import datetime

from core.models import MapLocation, School
from django.core.management.base import BaseCommand
from django.db import transaction

from users.models import CustomUser, Role


class Command(BaseCommand):
    help = 'Seeds the database with initial data for schools, roles, and users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            CustomUser.objects.all().delete()
            Role.objects.all().delete()
            School.objects.all().delete()
            MapLocation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared successfully'))

        self.stdout.write('Starting database seeding...')

        # Create map locations
        locations = [
            MapLocation.objects.create(latitude='-1.286389', longitude='36.817223'),
            MapLocation.objects.create(latitude='-1.292066', longitude='36.821945'),
            MapLocation.objects.create(latitude='-1.319194', longitude='36.829778'),
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {len(locations)} map locations'))

        # Create schools
        schools = [
            School.objects.create(
                name='Nairobi International School',
                year_started=1995,
                about='A leading international school offering world-class education',
                website='https://nairobischool.example.com',
                address='123 Nairobi Road, Nairobi, Kenya',
                map_location=locations[0],
                contact_email='info@nairobischool.example.com',
                contact_phone='+254712345678',
                logo_url='https://example.com/logos/nairobi-school.png'
            ),
            School.objects.create(
                name='Kenya Elite Academy',
                year_started=2005,
                about='Excellence in education with focus on STEM subjects',
                website='https://kenyanelite.example.com',
                address='456 Westlands Avenue, Nairobi, Kenya',
                map_location=locations[1],
                contact_email='contact@kenyanelite.example.com',
                contact_phone='+254723456789',
                logo_url='https://example.com/logos/kenya-elite.png'
            ),
            School.objects.create(
                name='Kilimani High School',
                year_started=1987,
                about='Traditional school with modern teaching methods',
                website='https://kilimanihigh.example.com',
                address='789 Kilimani Road, Nairobi, Kenya',
                map_location=locations[2],
                contact_email='admin@kilimanihigh.example.com',
                contact_phone='+254734567890'
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {len(schools)} schools'))

        # Create roles for each school
        role_templates = [
            {'name': 'Administrator', 'description': 'Full system access and management capabilities'},
            {'name': 'Teacher', 'description': 'Can manage classes, students, and grades'},
            {'name': 'Student', 'description': 'Can view courses and submit assignments'},
            {'name': 'Parent', 'description': 'Can view student progress and communicate with teachers'},
        ]

        roles_created = 0
        for school in schools:
            for role_data in role_templates:
                Role.objects.create(
                    school=school,
                    name=role_data['name'],
                    description=role_data['description']
                )
                roles_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {roles_created} roles'))

        # Create sample users for first school
        school = schools[0]
        admin_role = Role.objects.filter(school=school, name='Administrator').first()
        teacher_role = Role.objects.filter(school=school, name='Teacher').first()
        student_role = Role.objects.filter(school=school, name='Student').first()

        # Create admin user
        admin = CustomUser.objects.create_user(
            phone_number='+254700000001',
            email='admin@nairobischool.example.com',
            first_name='John',
            last_name='Administrator',
            password='admin123',
            status='active'
        )
        admin.schools.add(school)
        admin.roles.add(admin_role)

        # Create teacher users
        teachers = [
            {
                'phone_number': '+254700000002',
                'email': 'teacher1@nairobischool.example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'teacher123'
            },
            {
                'phone_number': '+254700000003',
                'email': 'teacher2@nairobischool.example.com',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'password': 'teacher123'
            },
        ]

        for teacher_data in teachers:
            teacher = CustomUser.objects.create_user(
                phone_number=teacher_data['phone_number'],
                email=teacher_data['email'],
                first_name=teacher_data['first_name'],
                last_name=teacher_data['last_name'],
                password=teacher_data['password'],
                status='active'
            )
            teacher.schools.add(school)
            teacher.roles.add(teacher_role)

        # Create student users
        students = [
            {
                'phone_number': '+254700000004',
                'email': 'student1@nairobischool.example.com',
                'first_name': 'Alice',
                'last_name': 'Brown',
                'password': 'student123'
            },
            {
                'phone_number': '+254700000005',
                'email': 'student2@nairobischool.example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'password': 'student123'
            },
            {
                'phone_number': '+254700000006',
                'email': 'student3@nairobischool.example.com',
                'first_name': 'Charlie',
                'last_name': 'Davis',
                'password': 'student123'
            },
        ]

        for student_data in students:
            student = CustomUser.objects.create_user(
                phone_number=student_data['phone_number'],
                email=student_data['email'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                password=student_data['password'],
                status='active'
            )
            student.schools.add(school)
            student.roles.add(student_role)

        users_created = 1 + len(teachers) + len(students)
        self.stdout.write(self.style.SUCCESS(f'Created {users_created} users'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('\nSample credentials:'))
        self.stdout.write(f'Admin: +254700000001 / admin123')
        self.stdout.write(f'Teacher: +254700000002 / teacher123')
        self.stdout.write(f'Student: +254700000004 / student123')
