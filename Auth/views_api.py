# students/api_views.py or Auth/views.py if you keep all API views together
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from Auth.models import CustomUser
from students.models import Schedule, Student, Subject
from .serializers import ScheduleSerializer, StudentSerializer, SubjectSerializer, UserLoginSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken  # For JWT authentication
from django.utils.translation import activate, gettext as _
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404




def test_translation_view(request):
    return JsonResponse({"message": _("Hello, World!")})


class SubjectListApiView(APIView):
    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
class ParentListApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Assuming you have a Parent model related to CustomUser
        parents = CustomUser.objects.filter(role='parent')  # Adjust the filter as per your role field
        serializer = UserLoginSerializer(parents, many=True)
        #enfants for this parent
        for parent in serializer.data:
            from students.models import Parent  # Make sure Parent model is imported

            parent_obj = get_object_or_404(Parent, id=parent['id'])
            children = parent_obj.children.all()
            print('children:', children)
            parent['children'] = [
                {
                    "id": child.id,
                    "first_name": child.first_name,
                    "last_name": child.last_name,
                    "class": child.student_class.name if child.student_class else None,
                    "enrollment_date": child.enrollment_date.strftime('%Y-%m-%d') if child.enrollment_date else None,
                }
                for child in children
            ]
        return Response(serializer.data)
    
class HomeworkViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer  # Assuming you have a serializer for Homework


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    def post(self, request):
        # Activate language from request parameters
        lang = request.GET.get('lang', 'en')
        activate(lang)

        # If user is already logged in
        if request.user.is_authenticated:
            return Response({
                "message": _("User {username} is already logged in.").format(username=request.user.username)
            }, status=status.HTTP_200_OK)

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            login(request, user)

            return Response({
                "message": _("Login successful!"),
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "image": user.image.url if user.image else None,
                    "access_token": access_token,
                    "students": [
                        {
                            "id": s.id,
                            "first_name": s.first_name,
                            "last_name": s.last_name,
                            "image": s.photo.url if s.photo else None,
                            "class": s.student_class.name if s.student_class else None
                        }
                        for s in getattr(getattr(user, "parent", None), "children", []).all()
                    ] if hasattr(user, "parent") else []
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#logout view Api
@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(APIView):
    def post(self, request):
        # If the user is not authenticated, send a message
        if not request.user.is_authenticated:
            return Response({
                "message": "User is not logged in."
            }, status=status.HTTP_200_OK)

        logout(request)
        return Response({
            "message": "Logout successful!"
        }, status=status.HTTP_200_OK)
    
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated] 


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer 
    permission_classes = [IsAuthenticated]  # Sécurisation API