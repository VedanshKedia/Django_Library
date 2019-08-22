from django.contrib import admin
from embed_video.admin import AdminVideoMixin
from .models import Item
# Register your models here.


class ItemAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)

#
# class ProfileAdmin(admin.ModelAdmin):
#     pass
#

# # admin.site.register(Profile, ProfileAdmin)
# admin.site.register(Profile)
