# students/serializers.py
from rest_framework import serializers
from .models import AppConfig, Student, Subject, Teacher, Classe, SessionYearModel, Attendance, Homework, Composition

class StudentSerializer(serializers.ModelSerializer):
    final_fee = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'nni', 'mobile', 'enrollment_date', 'student_class', 'has_discount', 'final_fee']

    def get_final_fee(self, obj):
        return obj.get_final_fee()

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = '__all__'

class SessionYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionYearModel
        fields = '__all__'
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name', 'class_enrolled', 'coefficient']
        
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'class_enrolled']


class AppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = ['school_name', 'address', 'contact_number', 'email', 'website', 'about']

class HomeworkSerializer(serializers.ModelSerializer):
    weighted_score = serializers.FloatField(source='get_weighted_score', read_only=True)  # Calcul du score pondéré

    class Meta:
        model = Homework
        fields = ['student', 'subject', 'due_date', 'description', 'submission_date', 'submitted', 'score', 'weighted_score']
class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = '__all__'