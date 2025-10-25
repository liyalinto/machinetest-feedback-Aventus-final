from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.models import User, update_last_login
from django.db import IntegrityError
from django.db.models import Q
from datetime import datetime
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Designation, Employee, FeedbackQuestion, FeedbackSubmission
from .serializers import (
    UserRegisterSerializer,
    DesignationSerializer,
    EmployeeSerializer,
    FeedbackQuestionSerializer,
    FeedbackSubmissionSerializer,
    FeedbackFilterSerializer
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Update last_login every time user logs in
        update_last_login(None, self.user)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        designation = getattr(user, '_designation', None)
        department = getattr(user, '_department', '')

        if not Employee.objects.filter(user=user).exists():
            try:
                Employee.objects.create(
                    user=user,
                    designation=designation,
                    department=department
                )
            except IntegrityError:
                pass
# Feedback Questions
class FeedbackQuestionListAPIView(generics.ListAPIView):
    serializer_class = FeedbackQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = FeedbackQuestion.objects.filter(is_active=True)
        ftype = self.request.query_params.get('type') or self.request.query_params.get('feedback_type')
        if ftype:
            qs = qs.filter(feedback_type=ftype)
        return qs


# Submit Feedback
class SubmitFeedbackAPIView(generics.CreateAPIView):
    serializer_class = FeedbackSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


# View Feedbacks
class EmployeeFeedbackListAPIView(generics.ListAPIView):
    serializer_class = FeedbackSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return FeedbackSubmission.objects.filter(submitted_by__id=employee_id).order_by('-created_at')

        if hasattr(self.request.user, 'employee_profile'):
            return FeedbackSubmission.objects.filter(
                submitted_by=self.request.user.employee_profile
            ).order_by('-created_at')

        return FeedbackSubmission.objects.none()
# Admin Feedback Filter



class AdminFeedbackFilterAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Filter feedback submissions by designation, department, and date range.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "designation": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Select designation (ID or name)",
                    enum=[d.name for d in Designation.objects.all()]  # dropdown
                ),
                "department": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Enter department name"
                ),
                "start_date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Filter feedbacks created after this date (YYYY-MM-DD)"
                ),
                "end_date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Filter feedbacks created before this date (YYYY-MM-DD)"
                ),
            },
            required=[],
        ),
        responses={200: FeedbackSubmissionSerializer(many=True)}
    )
    def post(self, request):
        designation = request.data.get('designation')
        department = request.data.get('department')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        qs = FeedbackSubmission.objects.all().select_related(
            'submitted_by__designation', 'target_employee__designation'
        ).prefetch_related('answers', 'answers__question')

        
        if designation:
            if str(designation).isdigit():
                qs = qs.filter(submitted_by__designation__id=int(designation))
            else:
                qs = qs.filter(submitted_by__designation__name__icontains=designation)

       
        if department:
            qs = qs.filter(submitted_by__department__icontains=department)

        
        if start_date:
            try:
                sd = datetime.fromisoformat(start_date)
                sd = timezone.make_aware(sd)
                qs = qs.filter(created_at__gte=sd)
            except ValueError:
                pass

        if end_date:
            try:
                ed = datetime.fromisoformat(end_date)
                ed = timezone.make_aware(ed)
                qs = qs.filter(created_at__lte=ed)
            except ValueError:
                pass

        serializer = FeedbackSubmissionSerializer(qs.order_by('-created_at'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Designation API
class DesignationListCreateAPIView(generics.ListCreateAPIView):
    """
    API to list all designations or create a new one.
    Only authenticated users can view.
    Only admins can create.
    """
    queryset = Designation.objects.all().order_by('id')
    serializer_class = DesignationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can add designations.")
        serializer.save() 
class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    