from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(group_name):
    def in_group(u):
        if u.is_authenticated and u.groups.filter(name=group_name).exists():
            return True
        raise PermissionDenied
    return user_passes_test(in_group)
