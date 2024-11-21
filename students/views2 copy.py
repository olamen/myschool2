# students/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import AppConfig, Homework, Student, Subject, Teacher, Class, SessionYearModel, Attendance, Composition
from .serializers import AppConfigSerializer, CompositionSerializer, HomeworkSerializer, StudentSerializer, SubjectSerializer, TeacherSerializer, ClassSerializer, SessionYearSerializer, AttendanceSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

class SessionYearViewSet(viewsets.ModelViewSet):
    queryset = SessionYearModel.objects.all()
    serializer_class = SessionYearSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        student_id = request.data.get('student_id')
        status = request.data.get('status')  # 'Present' ou 'Absent'
        class_id = request.data.get('class_id')
        
        # Vérifie si l'étudiant et la classe existent
        try:
            student = Student.objects.get(id=student_id)
            student_class = Class.objects.get(id=class_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=404)
        
        # Crée un enregistrement de présence
        attendance = Attendance(
            student=student,
            date=timezone.now().date(),  # Date du jour
            status=status,
            class_enrolled=student_class
        )
        attendance.save()

        return Response({"message": "Attendance marked successfully"})
    
class AppConfigViewSet(viewsets.ModelViewSet):
    queryset = AppConfig.objects.all()
    serializer_class = AppConfigSerializer
    def get(self, request):
        try:
            config = AppConfig.objects.all().first()  # Assumes only one configuration instance
            serializer = AppConfigSerializer(config)
            return Response(serializer.data)
        except AppConfig.DoesNotExist:
            return Response({"error": "AppConfig not found"}, status=404)
        

# Vue pour gérer les devoirs
class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer

    @action(detail=True, methods=['patch'])
    def update_score(self, request, pk=None):
        """Mettre à jour le score d'un devoir."""
        homework = self.get_object()
        score = request.data.get('score')  # Récupère le score du corps de la requête
        
        if score is not None:
            homework.score = score
            homework.save()
            return Response({"message": "Score updated successfully"})
        else:
            return Response({"error": "Score is required"}, status=400)

    @action(detail=True, methods=['get'])
    def weighted_score(self, request, pk=None):
        """Calculer le score pondéré basé sur le coefficient du sujet."""
        homework = self.get_object()
        weighted_score = homework.get_weighted_score()  # Méthode pour calculer le score pondéré
        return Response({"weighted_score": weighted_score})
    
class CompositionViewSet(viewsets.ModelViewSet):
    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

    @action(detail=True, methods=['patch'])
    def update_score(self, request, pk=None):
        """Mettre à jour le score d'une composition."""
        composition = self.get_object()
        score = request.data.get('score')  # Récupère le score du corps de la requête
        
        if score is not None:
            composition.score = score
            composition.save()
            return Response({"message": "Score updated successfully"})
        else:
            return Response({"error": "Score is required"}, status=400)

    @action(detail=True, methods=['get'])
    def weighted_score(self, request, pk=None):
        """Calculer le score pondéré basé sur le coefficient du sujet."""
        composition = self.get_object()
        weighted_score = composition.score * composition.subject.coefficient  # Score pondéré
        return Response({"weighted_score": weighted_score})