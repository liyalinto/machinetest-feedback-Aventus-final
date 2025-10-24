

# Register your models here.
from django.contrib import admin
from .models import Designation, Employee, FeedbackQuestion, FeedbackSubmission, FeedbackAnswer

admin.site.register(Designation)
admin.site.register(Employee)
admin.site.register(FeedbackQuestion)
admin.site.register(FeedbackSubmission)
admin.site.register(FeedbackAnswer)
