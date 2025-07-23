from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from students.models import Schedule, Classe, Subject, Teacher
from Auth.models import CustomUser
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from students.models import Schedule, Classe, Subject, Teacher
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

@login_required
def createorupdateschedule(request, schedule_id=None):
    """
    Single view to handle both creating and updating schedules
    """
    schedule = None
    if schedule_id:
        schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            class_id = request.POST.get('class_name')
            course_id = request.POST.get('course_name')
            professor_id = request.POST.get('professor')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            day_of_week = request.POST.get('day_of_week')
            
            # Validate required fields
            if not all([class_id, course_id, professor_id, start_time, end_time, day_of_week]):
                messages.error(request, 'All fields are required.')
                return redirect('createorupdateschedule', schedule_id=schedule_id)
            
            # Get related objects
            class_obj = get_object_or_404(Classe, id=class_id)
            course_obj = get_object_or_404(Subject, id=course_id)
            professor_obj = get_object_or_404(Teacher, id=professor_id)
            
            if schedule:
                # Update existing schedule
                schedule.class_name = class_obj
                schedule.course_name = course_obj
                schedule.professor = professor_obj
                schedule.start_time = start_time
                schedule.end_time = end_time
                schedule.day_of_week = day_of_week
                schedule.save()
                messages.success(request, 'Schedule updated successfully!')
            else:
                # Create new schedule
                schedule = Schedule.objects.create(
                    user=request.user,
                    class_name=class_obj,
                    course_name=course_obj,
                    professor=professor_obj,
                    start_time=start_time,
                    end_time=end_time,
                    day_of_week=day_of_week
                )
                messages.success(request, 'Schedule created successfully!')
            
            return redirect('schedule_list')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('createorupdateschedule', schedule_id=schedule_id)
    
    # GET request - render form
    context = {
        'schedule': schedule,
        'classes': Classe.objects.filter(is_active=True),
        'subjects': Subject.objects.filter(is_active=True),
        'teachers': Teacher.objects.filter(is_active=True),
        'day_choices': Schedule.DAY_CHOICES,
        'is_edit': bool(schedule),
    }
    return render(request, 'students/schedule/create_update.html', context)

@login_required
def schedule_list(request):
    """
    List all schedules
    """
    schedules = Schedule.objects.all().order_by('day_of_week', 'start_time')
    context = {
        'schedules': schedules,
    }
    return render(request, 'students/schedule/list.html', context)

@login_required
def schedule_detail(request, schedule_id):
    """
    View schedule details
    """
    schedule = get_object_or_404(Schedule, id=schedule_id)
    context = {
        'schedule': schedule,
    }
    return render(request, 'students/schedule/detail.html', context)

@login_required
def delete_schedule(request, schedule_id):
    """
    Delete a schedule
    """
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('schedule_list')
    
    context = {
        'schedule': schedule,
    }
    return render(request, 'students/schedule/delete_confirm.html', context)

# AJAX views for dynamic loading
@login_required
def get_subjects_by_grade_ajax(request, grade_id):
    """
    AJAX view to get subjects by grade
    """
    try:
        subjects = Subject.objects.filter(grade_id=grade_id, is_active=True)
        data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'success': True, 'subjects': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_teachers_by_subject_ajax(request, subject_id):
    """
    AJAX view to get teachers by subject
    """
    try:
        teachers = Teacher.objects.filter(subject=subject_id, is_active=True)
        data = [{'id': teacher.id, 'name': teacher.name} for teacher in teachers]
        return JsonResponse({'success': True, 'teachers': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    



# ... existing views ...

@login_required
def print_schedule_options(request):
    """
    Display print options for schedules
    """
    context = {
        'classes': Classe.objects.filter(is_active=True),
        'current_date': timezone.now().date(),
    }
    return render(request, 'students/schedule/print_options.html', context)

@login_required
def print_schedule_by_day(request):
    """
    Print schedule for a specific day
    """
    date_str = request.GET.get('date')
    class_id = request.GET.get('class_id')
    
    if not date_str:
        date_str = timezone.now().date().isoformat()
    
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    day_of_week = selected_date.strftime('%A').upper()
    
    # Map day names to your model choices
    day_mapping = {
        'MONDAY': 'monday',
        'TUESDAY': 'tuesday', 
        'WEDNESDAY': 'wednesday',
        'THURSDAY': 'thursday',
        'FRIDAY': 'friday',
        'SATURDAY': 'saturday',
        'SUNDAY': 'sunday'
    }
    
    schedules = Schedule.objects.filter(
        day_of_week=day_mapping.get(day_of_week, day_of_week.lower())
    ).order_by('start_time')
    
    if class_id:
        schedules = schedules.filter(class_name_id=class_id)
    
    context = {
        'schedules': schedules,
        'selected_date': selected_date,
        'day_name': selected_date.strftime('%A'),
        'class_filter': class_id,
        'selected_class': Classe.objects.get(id=class_id) if class_id else None,
    }
    
    if request.GET.get('format') == 'pdf':
        return generate_day_schedule_pdf(schedules, selected_date, context.get('selected_class'))
    
    return render(request, 'students/schedule/print_day.html', context)

@login_required
def print_schedule_by_week(request):
    """
    Print schedule for a specific week
    """
    date_str = request.GET.get('date')
    class_id = request.GET.get('class_id')
    
    if not date_str:
        selected_date = timezone.now().date()
    else:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Get start of week (Monday)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get all schedules for the week
    week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    schedules = Schedule.objects.filter(day_of_week__in=week_days).order_by('day_of_week', 'start_time')
    
    if class_id:
        schedules = schedules.filter(class_name_id=class_id)
    
    # Group schedules by day
    weekly_schedule = {}
    for day in week_days:
        weekly_schedule[day] = schedules.filter(day_of_week=day)
    
    context = {
        'weekly_schedule': weekly_schedule,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'week_dates': [start_of_week + timedelta(days=i) for i in range(7)],
        'class_filter': class_id,
        'selected_class': Classe.objects.get(id=class_id) if class_id else None,
    }
    
    if request.GET.get('format') == 'pdf':
        return generate_week_schedule_pdf(weekly_schedule, start_of_week, end_of_week, context.get('selected_class'))
    
    return render(request, 'students/schedule/print_week.html', context)

@login_required
def print_schedule_by_month(request):
    """
    Print schedule for a specific month
    """
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    class_id = request.GET.get('class_id')
    
    # Get all schedules
    schedules = Schedule.objects.all().order_by('day_of_week', 'start_time')
    
    if class_id:
        schedules = schedules.filter(class_name_id=class_id)
    
    # Get calendar for the month
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Group schedules by day of week
    weekly_schedule = {}
    week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in week_days:
        weekly_schedule[day] = schedules.filter(day_of_week=day)
    
    context = {
        'weekly_schedule': weekly_schedule,
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': month_name,
        'class_filter': class_id,
        'selected_class': Classe.objects.get(id=class_id) if class_id else None,
        'schedules': schedules,
    }
    
    if request.GET.get('format') == 'pdf':
        return generate_month_schedule_pdf(weekly_schedule, year, month, context.get('selected_class'))
    
    return render(request, 'students/schedule/print_month.html', context)

def generate_day_schedule_pdf(schedules, selected_date, selected_class=None):
    """
    Generate PDF for day schedule
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="schedule_{selected_date}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    title_text = f"Daily Schedule - {selected_date.strftime('%A, %B %d, %Y')}"
    if selected_class:
        title_text += f" - {selected_class.name}"
    
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))
    
    if schedules:
        # Create table data
        data = [['Time', 'Subject', 'Professor', 'Class']]
        for schedule in schedules:
            data.append([
                f"{schedule.start_time} - {schedule.end_time}",
                schedule.course_name.name,
                schedule.professor.name,
                schedule.class_name.name
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph("No classes scheduled for this day.", styles['Normal']))
    
    doc.build(story)
    return response

def generate_week_schedule_pdf(weekly_schedule, start_of_week, end_of_week, selected_class=None):
    """
    Generate PDF for week schedule
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="weekly_schedule_{start_of_week}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    title_text = f"Weekly Schedule - {start_of_week.strftime('%B %d')} to {end_of_week.strftime('%B %d, %Y')}"
    if selected_class:
        title_text += f" - {selected_class.name}"
    
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))
    
    # Create weekly table
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_keys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    data = [days]  # Header row
    
    # Find maximum number of classes in any day
    max_classes = max([len(weekly_schedule.get(day, [])) for day in day_keys]) or 1
    
    for i in range(max_classes):
        row = []
        for day_key in day_keys:
            schedules = weekly_schedule.get(day_key, [])
            if i < len(schedules):
                schedule = schedules[i]
                cell_text = f"{schedule.start_time}-{schedule.end_time}\n{schedule.course_name.name}\n{schedule.professor.name}"
                if not selected_class:
                    cell_text += f"\n{schedule.class_name.name}"
            else:
                cell_text = ""
            row.append(cell_text)
        data.append(row)
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(table)
    doc.build(story)
    return response

def generate_month_schedule_pdf(weekly_schedule, year, month, selected_class=None):
    """
    Generate PDF for month schedule
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly_schedule_{year}_{month:02d}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    title_text = f"Monthly Schedule - {calendar.month_name[month]} {year}"
    if selected_class:
        title_text += f" - {selected_class.name}"
    
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))
    
    # Add weekly schedule summary
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_keys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for i, day in enumerate(days):
        day_key = day_keys[i]
        schedules = weekly_schedule.get(day_key, [])
        
        if schedules:
            story.append(Paragraph(f"<b>{day}</b>", styles['Heading3']))
            
            day_data = [['Time', 'Subject', 'Professor', 'Class']]
            for schedule in schedules:
                day_data.append([
                    f"{schedule.start_time} - {schedule.end_time}",
                    schedule.course_name.name,
                    schedule.professor.name,
                    schedule.class_name.name if not selected_class else ""
                ])
            
            day_table = Table(day_data)
            day_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(day_table)
            story.append(Spacer(1, 15))
    
    doc.build(story)
    return response