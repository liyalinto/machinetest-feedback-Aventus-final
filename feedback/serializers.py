


from django.contrib.auth.models import User
from .models import Designation, Employee, FeedbackQuestion, FeedbackSubmission, FeedbackAnswer
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Employee, Designation


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    department = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=100
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'designation_id',
            'department',
        )

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        designation = validated_data.pop('designation_id', None)
        department = validated_data.pop('department', None)

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        # Always create or update the employee profile safely
        employee, created = Employee.objects.get_or_create(user=user)
        if designation:
            employee.designation = designation
        if department:
            employee.department = department
        employee.save()

        return user


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'name']
        ref_name = "DesignationSerializerMain"



class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    designation = DesignationSerializer(read_only=True)
    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        write_only=True,
        source='designation',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_id', 'designation', 'designation_id', 'department', 'employee_code']
        read_only_fields = ['id', 'user']



class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = ['id', 'text', 'feedback_type', 'is_active', 'order']





class FeedbackAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=FeedbackQuestion.objects.filter(is_active=True),
        source='question',
        write_only=True
    )
    question = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FeedbackAnswer
        fields = ['question', 'question_id', 'rating', 'comment']


class FeedbackSubmissionSerializer(serializers.ModelSerializer):
    answers = FeedbackAnswerSerializer(many=True)
    target_employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='target_employee',
        write_only=True
    )
    submitted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    submitted_by_employee = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedbackSubmission
        fields = [
            'id',
            'submitted_by',
            'submitted_by_employee',
            'target_employee_id',
            'created_at',
            'answers'
        ]
        read_only_fields = ['id', 'created_at', 'submitted_by', 'submitted_by_employee']

    def get_submitted_by_employee(self, obj):
        return str(obj.submitted_by)

    def create(self, validated_data):
        """Create a feedback submission with multiple answers."""
        answers_data = validated_data.pop('answers', [])
        request = self.context.get('request')

     
        if not hasattr(request.user, 'employee_profile'):
            raise serializers.ValidationError("Submitting user must have an Employee profile.")

      
        submitted_by = request.user.employee_profile
        submission = FeedbackSubmission.objects.create(submitted_by=submitted_by, **validated_data)

       
        feedback_answers = [
            FeedbackAnswer(
                submission=submission,
                question=ans['question'],
                rating=ans['rating'],
                comment=ans.get('comment', '')
            )
            for ans in answers_data
        ]
        FeedbackAnswer.objects.bulk_create(feedback_answers)

        return submission







