# # feedback/urls.py
# from django.urls import path
# from .views import (
#     RegisterView, FeedbackQuestionListAPIView, SubmitFeedbackAPIView,
#     EmployeeFeedbackListAPIView, AdminFeedbackFilterAPIView
# )
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path('auth/register/', RegisterView.as_view(), name='register'),
#     path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

#     path('questions/', FeedbackQuestionListAPIView.as_view(), name='feedback-questions'),
#     path('feedback/submit/', SubmitFeedbackAPIView.as_view(), name='submit-feedback'),
#     path('feedback/my/', EmployeeFeedbackListAPIView.as_view(), name='my-feedback'),
#     path('feedback/admin/', AdminFeedbackFilterAPIView.as_view(), name='admin-feedback'),
# ]
# feedback/urls.py
from django.urls import path
from .views import (
    RegisterView, FeedbackQuestionListAPIView, SubmitFeedbackAPIView,
    EmployeeFeedbackListAPIView, AdminFeedbackFilterAPIView, EmployeeListAPIView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import DesignationListCreateAPIView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('questions/', FeedbackQuestionListAPIView.as_view(), name='feedback-questions'),
    path('feedback/submit/', SubmitFeedbackAPIView.as_view(), name='submit-feedback'),
    path('feedback/my/', EmployeeFeedbackListAPIView.as_view(), name='my-feedback'),
    path('feedback/admin/', AdminFeedbackFilterAPIView.as_view(), name='admin-feedback'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('designations/', DesignationListCreateAPIView.as_view(), name='designation-list-create'),

  
]