# Generated by Django 5.1.3 on 2024-11-18 15:10

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('contact_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('website', models.URLField(blank=True, null=True)),
                ('about', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('monthly_salary_fee', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SessionYearModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_start_year', models.DateField()),
                ('session_end_year', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=50)),
                ('enrollment_date', models.DateField()),
                ('salary', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('nni', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10)])),
                ('mobile', models.CharField(max_length=40)),
                ('enrollment_date', models.DateField(auto_now_add=True)),
                ('has_discount', models.BooleanField(default=False)),
                ('gender', models.CharField(choices=[('M', 'Garçon'), ('F', 'Fille')], default='M', max_length=1)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='student_photos/')),
                ('student_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='students.class')),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField(blank=True, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='parent_photos/')),
                ('children', models.ManyToManyField(related_name='parents', to='students.student')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('status', models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent')], default='Absent', max_length=10)),
                ('class_enrolled', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='students.student')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('coefficient', models.DecimalField(decimal_places=1, default=1, max_digits=3)),
                ('class_enrolled', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='students.class')),
            ],
        ),
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Devoir', max_length=100)),
                ('due_date', models.DateField()),
                ('description', models.TextField()),
                ('submission_date', models.DateField(blank=True, null=True)),
                ('submitted', models.BooleanField(default=False)),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='students.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='students.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Composition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Composition', max_length=100)),
                ('exam_date', models.DateField()),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compositions', to='students.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compositions', to='students.subject')),
            ],
        ),
    ]
