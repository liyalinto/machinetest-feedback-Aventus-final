
# Create your models here.
# feedback/models.py
from django.db import models
from django.contrib.auth.models import User

class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.designation})"

class FeedbackQuestion(models.Model):
    FEEDBACK_TYPE_CHOICES = (
        ('employee', 'Employee'),
        ('trainer', 'Trainer'),
    )
    text = models.TextField()
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"[{self.feedback_type}] {self.text[:50]}"

class FeedbackSubmission(models.Model):
    submitted_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='submissions')
    target_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='feedback_received', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # optional: feedback cycle, tags, is_anonymous flag etc.

    def __str__(self):
        return f"Submission {self.id} by {self.submitted_by}"

class FeedbackAnswer(models.Model):
    submission = models.ForeignKey(FeedbackSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField()  # e.g., 1-5
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Answer q:{self.question.id} rating:{self.rating}"

