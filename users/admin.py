from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
	("Profile", {
			"fields": ("username","nickname",),
			"classes": ("wide",),
		},
	),
	("Permissions",{
			"fields": (
				"is_active",
				"is_staff",
				"is_superuser",
				# "user_permissions",
			),
		},
	),
	("Important Dates", {
			"fields": ("password","last_login", "date_joined", "uuid"),
			"classes": ("collapse",),   #접었다폈다
		},
	),
)
    list_display = ("id","nickname","username", "is_superuser","age",'gender','uuid')
    list_filter = ("is_superuser",'age','gender')
    search_fields = ("username","nickname","uuid",)
    ordering = ("id",)
    # filter_horizontal = (
    #     "groups",
    #     "user_permissions",
    # )
	
    readonly_fields = ("date_joined", "last_login",)

