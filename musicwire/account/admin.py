from django.contrib import admin

from musicwire.account.models import UserProfile


class UserProfileModelAdmin(admin.ModelAdmin):
    list_display = 'username', 'email'
    exclude = 'password',

    class Meta:
        fields = 'username', 'email'


admin.site.register(UserProfile, UserProfileModelAdmin)
