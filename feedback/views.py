from django.shortcuts import render

# Create your views here.
# feedback/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Designation, Employee, FeedbackQuestion, FeedbackSubmission
from .serializers import (
    UserRegisterSerializer, DesignationSerializer, EmployeeSerializer,
    FeedbackQuestionSerializer, FeedbackSubmissionSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from datetime import datetime
from .models import Employee
from .serializers import EmployeeSerializer
# Public: register
class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

# JWT login: use simplejwt's TokenObtainPairView (no extra code needed)
# in urls.py we'll import TokenObtainPairView and TokenRefreshView

# List feedback questions (filter by type)
class FeedbackQuestionListAPIView(generics.ListAPIView):
    serializer_class = FeedbackQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]  # spec says only authenticated can access protected endpoints
    def get_queryset(self):
        qs = FeedbackQuestion.objects.filter(is_active=True)
        ftype = self.request.query_params.get('type') or self.request.query_params.get('feedback_type')
        if ftype:
            qs = qs.filter(feedback_type=ftype)
        return qs

# Submit feedback (create submission + nested answers)
class SubmitFeedbackAPIView(generics.CreateAPIView):
    serializer_class = FeedbackSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

# View feedback for a specific employee (by employee id)
class EmployeeFeedbackListAPIView(generics.ListAPIView):
    serializer_class = FeedbackSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # if user passes ?employee_id= or use current user
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return FeedbackSubmission.objects.filter(submitted_by__id=employee_id).order_by('-created_at')
        # default: feedbacks submitted by current user's employee profile
        if hasattr(self.request.user, 'employee_profile'):
            return FeedbackSubmission.objects.filter(submitted_by=self.request.user.employee_profile).order_by('-created_at')
        return FeedbackSubmission.objects.none()

# Admin view with filters: designation, department, date range
class AdminFeedbackFilterAPIView(generics.ListAPIView):
    serializer_class = FeedbackSubmissionSerializer
    permission_classes = [permissions.IsAdminUser]  # only admin by default

    def get_queryset(self):
        qs = FeedbackSubmission.objects.all().select_related('submitted_by__designation','target_employee__designation').prefetch_related('answers','answers__question')
        designation = self.request.query_params.get('designation')  # designation id or name supported
        department = self.request.query_params.get('department')
        start_date = self.request.query_params.get('start_date')  # expected YYYY-MM-DD
        end_date = self.request.query_params.get('end_date')

        if designation:
            # attempt numeric id else name
            if designation.isdigit():
                qs = qs.filter(submitted_by__designation__id=int(designation))
            else:
                qs = qs.filter(submitted_by__designation__name__icontains=designation)

        if department:
            qs = qs.filter(submitted_by__department__icontains=department)

        if start_date:
            try:
                sd = datetime.fromisoformat(start_date)
                qs = qs.filter(created_at__gte=sd)
            except ValueError:
                pass
        if end_date:
            try:
                ed = datetime.fromisoformat(end_date)
                qs = qs.filter(created_at__lte=ed)
            except ValueError:
                pass

        return qs.order_by('-created_at')
# feedback/views.py


# class EmployeeListAPIView(generics.ListAPIView):
#     """
#     API to view all employees with optional filters.
#     Accessible to authenticated users (you can restrict to admin if needed).
#     """
#     serializer_class = EmployeeSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         queryset = Employee.objects.select_related('user', 'designation').all()

#         # Optional filters
#         designation = self.request.query_params.get('designation')
#         department = self.request.query_params.get('department')
#         user_id = self.request.query_params.get('user_id')

#         if designation:
#             # Filter by designation name or id
#             if designation.isdigit():
#                 queryset = queryset.filter(designation__id=int(designation))
#             else:
#                 queryset = queryset.filter(designation__name__icontains=designation)

#         if department:
#             queryset = queryset.filter(department__icontains=department)

#         if user_id:
#             queryset = queryset.filter(user__id=user_id)

#         return queryset.order_by('user__first_name')
class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all().select_related('username', 'designation')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]  