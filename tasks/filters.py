import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    priority = django_filters.CharFilter(field_name="priority")

    start_date_after = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_before = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")

    end_date_after = django_filters.DateFilter(field_name="end_date", lookup_expr="gte")
    end_date_before = django_filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = [
            "status",
            "priority",
            "start_date_after",
            "start_date_before",
            "end_date_after",
            "end_date_before",
        ]