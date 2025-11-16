from .models import Task, TaskCategory
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class TaskCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TaskCategory
        fields = "__all__"
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user', None)  
        return super().update(instance, validated_data)        


class TaskSerializer(serializers.ModelSerializer):
    creator_is_superuser = serializers.SerializerMethodField()
    category = TaskCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.none(),
        source="category",
        write_only=True,
        required=False
    )
    class Meta:
        model = Task
        fields = [
            "id", "title", "description",
            "start_date", "end_date",
            "priority", "status",
            "creator", "assignee",
            "category", "category_id",
            "is_today",
            "created_at", "updated_at", "creator_is_superuser",
        ]
        read_only_fields = ["id", "creator", "created_at"]


    def get_creator_is_superuser(self, obj):
        return obj.creator.is_superuser
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            
            self.fields["category_id"].queryset = TaskCategory.objects.filter(user=request.user)

            if request.user.is_superuser:
                self.fields["assignee"].queryset = User.objects.filter(is_staff=True)
            
            else:
                self.fields["assignee"].queryset = User.objects.filter(id=request.user.id)