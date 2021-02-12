from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User
# from .forms import CustomUserCreationForm


# class CustomUserAdmin(UserAdmin):
#     model = User
#     add_form = CustomUserCreationForm

#     fieldsets = (
#         *UserAdmin.fieldsets,
#         (
#             'user is guest', {
#                 'fields': (
#                     'guest',
#                 )
#             }
#         )
#     )


# admin.site.register(User, CustomUserAdmin)

#ading profile of user
from .models import Profile

admin.site.register(Profile)