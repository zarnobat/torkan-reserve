from django.shortcuts import render
from .models import TaskCategory, Task
from .permissions import CanCreateTask
from .serializer import TaskCategorySerializer, TaskSerializer 


from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils.timezone import localdate
from django.db.models import Q
from django.contrib.auth import get_user_model



User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    if request.user.is_superuser:
        users = User.objects.filter(is_staff=True)
    else:
        users = User.objects.filter(pk=request.user.pk)
    data = [{"name": u.name, "phone_number": u.phone_number} for u in users]
    return Response(data)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateTask]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Task.objects.filter(creator=user)

        return Task.objects.filter(
            Q(creator=user) | (Q(creator__is_superuser=True) & Q(assignee=user))
        ).order_by('-created_at')


    def perform_create(self, serializer):
        user = self.request.user
        assignee = serializer.validated_data.get("assignee")

        if assignee is None:
            raise PermissionDenied("انتخاب انجام‌دهنده الزامی است.")
        
        if not user.is_superuser:
            if assignee != user:
                raise PermissionDenied("کارمند فقط می‌تواند برای خودش تسک ایجاد کند.")

        else:
            if not assignee.is_staff:
                raise PermissionDenied("مدیر فقط می‌تواند برای خودش و کارمندان تسک ایجاد کند.")

        serializer.save(creator=user)


    @action(detail=False, methods=["GET"])
    def today(self, request):
        today = localdate()
        qs = self.get_queryset().filter(
            start_date__lte=today
        ).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def set_status(self, request, pk=None):
        task = self.get_object()
        user = request.user

        
        if not (user.is_staff or user.is_superuser) and task.assignee != user:
            return Response({"error": "اجازه تغییر وضعیت این تسک را ندارید."}, status=403)

        new_status = request.data.get("status")
        if new_status not in [choice[0] for choice in Task.Status.choices]:
            return Response({"error": "وضعیت نامعتبر است!"}, status=400)

        task.status = new_status
        task.save()
        return Response({"status": "updated"})
    

class TaskCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TaskCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskCategory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def dashboard_view(request):
    return render(request, "tasks/dashboard.html")

