import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'status', 'assigned_to']