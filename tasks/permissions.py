from rest_framework.permissions import BasePermission

class CanCreateTask(BasePermission):

    def has_permission(self, request, view):
        
        return True