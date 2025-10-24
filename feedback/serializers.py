# feedback/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Designation, Employee, FeedbackQuestion, FeedbackSubmission, FeedbackAnswer


# class UserRegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=6)
#     class Meta:
#         model = User
#         fields = ('id','username','email','password','first_name','last_name')

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         # Optionally create an Employee record automatically (if required)
#         Employee.objects.create(user=user)
#         return user



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        source='employee_profile.designation',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'designation_id')

    def create(self, validated_data):
        password = validated_data.pop('password')
        employee_data = validated_data.pop('employee_profile', {})  # extract nested employee data if any

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create related Employee record
        designation = employee_data.get('designation') if employee_data else None
        Employee.objects.create(user=user, designation=designation)
        return user



class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id','name']

class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    designation = DesignationSerializer(read_only=True)
    designation_id = serializers.PrimaryKeyRelatedField(queryset=Designation.objects.all(), write_only=True, source='designation', required=False, allow_null=True)

    class Meta:
        model = Employee
        fields = ['id','user','user_id','designation','designation_id','department','employee_code']
        read_only_fields = ['id','user']

class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = ['id','text','feedback_type','is_active','order']

class FeedbackAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(queryset=FeedbackQuestion.objects.filter(is_active=True), source='question', write_only=True)
    question = FeedbackQuestionSerializer(read_only=True)

    class Meta:
        model = FeedbackAnswer
        fields = ['id','question','question_id','rating','comment']

class FeedbackSubmissionSerializer(serializers.ModelSerializer):
    answers = FeedbackAnswerSerializer(many=True)
    submitted_by = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    target_employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='target_employee', write_only=True, required=False, allow_null=True)
    submitted_by_employee = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedbackSubmission
        fields = ['id','submitted_by','submitted_by_employee','target_employee_id','created_at','answers']
        read_only_fields = ['id','created_at','submitted_by','submitted_by_employee']

    def get_submitted_by_employee(self, obj):
        return str(obj.submitted_by)

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        # determine employee who is submitting from context (request.user)
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee_profile'):
            submitted_by = request.user.employee_profile
        else:
            # fallback - raise
            raise serializers.ValidationError("Submitting user must have an Employee profile.")
        submission = FeedbackSubmission.objects.create(submitted_by=submitted_by, **validated_data)
        for ans in answers_data:
            FeedbackAnswer.objects.create(
                submission=submission,
                question=ans['question'],
                rating=ans['rating'],
                comment=ans.get('comment','')
            )
        return submission
class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'name']
        ref_name = "DesignationSerializerMain"
