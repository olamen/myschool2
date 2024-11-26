# Generated by Django 5.1.3 on 2024-11-26 17:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0002_classe_grade_subject_is_active_teacher_is_active_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('school_year', models.CharField(max_length=9)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='NoteStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coefficient', models.DecimalField(decimal_places=2, default=1.0, max_digits=4)),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('classe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.classe')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='notes.exam')),
                ('sessionyear', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.sessionyearmodel')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='students.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.subject')),
            ],
        ),
    ]