from rest_framework.permissions import BasePermission


class IsMemberOfSchool(BasePermission):
    message = "You are not a member of this school."

    def has_permission(self, request, view):
        school_id = view.kwargs.get("school_pk") or view.kwargs.get("school_id")

        if not school_id or not request.user.is_authenticated:
            return False

        return request.user.schools.filter(id=school_id).exists()

    #def has_object_permission(self, request, view, obj):
        #return True
        #return obj.school.users.filter(id=request.user.id).exists()
