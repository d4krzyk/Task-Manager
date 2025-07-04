from django.shortcuts import render
from rest_framework import viewsets, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, TaskHistory
from .serializers import TaskSerializer, TaskHistorySerializer, RegisterSerializer
from .filters import TaskFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    @swagger_auto_schema(
        operation_description="Rejestracja nowego użytkownika.",
        responses={201: "Użytkownik zarejestrowany", 400: "Błąd walidacji"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilter
    search_fields = ['name', 'description']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description="ID zadania", type=openapi.TYPE_INTEGER),
        openapi.Parameter('name', openapi.IN_QUERY, description="Nazwa (fragment)", type=openapi.TYPE_STRING),
        openapi.Parameter('description', openapi.IN_QUERY, description="Opis (fragment)", type=openapi.TYPE_STRING),
        openapi.Parameter('status', openapi.IN_QUERY, description="Status", type=openapi.TYPE_STRING),
        openapi.Parameter('assigned_to', openapi.IN_QUERY, description="ID użytkownika", type=openapi.TYPE_INTEGER),
        openapi.Parameter('search', openapi.IN_QUERY, description="Wyszukiwanie tekstowe", type=openapi.TYPE_STRING),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Zapisanie do TaskHistory każdej zmianę nazwy, opisu, statusu lub przypisanego użytkownika zadania
    def perform_history_log(self, task, request, user=None):
        try:
            old_task = Task.objects.get(pk=task.pk)
        except Task.DoesNotExist:
            old_task = None

        fields = ['name', 'description', 'status', 'assigned_to']
        for field in fields:
            old_value = getattr(old_task, field, None) if old_task else None
            new_value = getattr(task, field, None)

            if field == 'assigned_to':
                old_value = old_value.id if old_value else None
                new_value = new_value.id if new_value else None
            if old_value != new_value:
                TaskHistory.objects.create(
                    task=task,
                    task_id_snapshot=task.id,
                    changed_by=request.user if request.user.is_authenticated else None,
                    changed_by_username=request.user.username if request.user.is_authenticated else None,
                    field=field,
                    old_value=old_value,
                    new_value=new_value
                )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        task = Task.objects.get(pk=response.data['id'])
        # Rejestracja początkowego stanu zadania
        for field in ['name', 'description', 'status', 'assigned_to']:
            value = getattr(task, field, None)
            if field == 'assigned_to':
                value = value.id if value else None
            TaskHistory.objects.create(
                task=task,
                task_id_snapshot=task.id,
                changed_by=request.user if request.user.is_authenticated else None,
                changed_by_username=request.user.username if request.user.is_authenticated else None,
                field=field,
                old_value=None,
                new_value=value
            )
        return response

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        # Rejestracja zmian w polach zadania
        old_values = {field: getattr(task, field, None) for field in ['name', 'description', 'status', 'assigned_to']}
        response = super().update(request, *args, **kwargs)
        task.refresh_from_db()
        for field in ['name', 'description', 'status', 'assigned_to']:
            old_value = old_values[field]
            new_value = getattr(task, field, None)
            if field == 'assigned_to':
                old_value = old_value.id if old_value else None
                new_value = new_value.id if new_value else None
            if old_value != new_value:
                TaskHistory.objects.create(
                    task=task,
                    task_id_snapshot=task.id,
                    changed_by=request.user if request.user.is_authenticated else None,
                    changed_by_username=request.user.username if request.user.is_authenticated else None,
                    field=field,
                    old_value=old_value,
                    new_value=new_value
                )
        return response


    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        # Rejestracja usunięcia zadania
        for field in ['name', 'description', 'status', 'assigned_to']:
            old_value = getattr(task, field, None)
            if field == 'assigned_to':
                old_value = old_value.id if old_value else None
            TaskHistory.objects.create(
                task=task,
                task_id_snapshot=task.id,
                changed_by=request.user if request.user.is_authenticated else None,
                changed_by_username=request.user.username if request.user.is_authenticated else None,
                field=field,
                old_value=old_value,
                new_value=None
            )
        return super().destroy(request, *args, **kwargs)

class TaskHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'task_id_snapshot', 'changed_by', 'changed_by_username', 'field', 'old_value', 'new_value']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('task', openapi.IN_QUERY, description="ID zadania", type=openapi.TYPE_INTEGER),
        openapi.Parameter('task_id_snapshot', openapi.IN_QUERY, description="ID zadania (zrzut backupowy)", type=openapi.TYPE_INTEGER),
        openapi.Parameter('changed_by', openapi.IN_QUERY, description="ID użytkownika", type=openapi.TYPE_INTEGER),
        openapi.Parameter('changed_by_username', openapi.IN_QUERY, description="Nazwa użytkownika",type=openapi.TYPE_STRING),
        openapi.Parameter('timestamp_from', openapi.IN_QUERY, description="Od daty (ISO 8601)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        openapi.Parameter('timestamp_to', openapi.IN_QUERY, description="Do daty (ISO 8601)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        ts_from = self.request.query_params.get('timestamp_from')
        ts_to = self.request.query_params.get('timestamp_to')
        if ts_from:
            dt_from = parse_datetime(ts_from)
            if dt_from:
                qs = qs.filter(timestamp__gte=dt_from)
        if ts_to:
            dt_to = parse_datetime(ts_to)
            if dt_to:
                qs = qs.filter(timestamp__lte=dt_to)
        return qs