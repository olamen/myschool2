from rest_framework import serializers
from django.contrib.auth import authenticate

from students.models import Schedule, Student, Subject
from .models import CustomUser

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials. Please try again.")
        
        if not user.is_approved:  # Ensure account is approved
            raise serializers.ValidationError("Your account is not approved yet.")
        
        return {"user": user}


#StudentSerializer
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'nni', 'mobile', 'student_class', 'enrollment_date', 'image']  # Add other fields if needed


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']  # Add other fields if needed

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'