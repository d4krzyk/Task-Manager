from rest_framework import serializers
from .models import Task, TaskHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'status', 'assigned_to']

class TaskHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskHistory
        fields = ['id', 'task', 'task_id_snapshot', 'changed_by', 'changed_by_username', 'timestamp', 'field', 'old_value', 'new_value']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Hasła nie są takie same.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user