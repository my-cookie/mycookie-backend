from django.contrib import admin
from .models import User, TemporalNickname, BannedUser, SiteInfo, PreferenceInfo
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
    list_display = ("id","nickname","username", "is_superuser", "is_staff", "age",'gender','uuid')
    list_filter = ("is_superuser","is_staff",'age','gender')
    search_fields = ("username","nickname","uuid",)
    ordering = ("id",)
    # filter_horizontal = (
    #     "groups",
    #     "user_permissions",
    # )
	
    readonly_fields = ("date_joined", "last_login",)



@admin.register(TemporalNickname)
class TemporalNicknameAdmin(admin.ModelAdmin):  
    list_display = ('id', 'user', 'nickname', 'created_at')
   
    
@admin.register(BannedUser)
class BannedUserAdmin(admin.ModelAdmin):  
    list_display = ('id', 'username', 'created_at', )
    
@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):  
    list_display = ('id', 'today_user', 'realtime_user', 'current_user', 'total_user', 'created_at', 'updated_at')

@admin.register(PreferenceInfo)
class PreferenceInfoAdmin(admin.ModelAdmin):  
    list_display = ('id', 'flavor', 'flavor_num', 'age', 'gender', )
  