
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
    employee_code = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
       
        if not self.employee_code:
            last_employee = Employee.objects.order_by('-id').first()
            next_id = 1 if not last_employee else last_employee.id + 1
            self.employee_code = f"EMP{next_id:04d}"  
        super().save(*args, **kwargs)

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
    

    def __str__(self):
        return f"Submission {self.id} by {self.submitted_by}"

class FeedbackAnswer(models.Model):
    submission = models.ForeignKey(FeedbackSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Answer q:{self.question.id} rating:{self.rating}"