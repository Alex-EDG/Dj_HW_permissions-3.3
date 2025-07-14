from django.contrib import admin
from advertisements.models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'description', 'status', 'creator', 'created_at', 'updated_at')
    list_filter = ['title', 'description', 'status', 'creator', 'created_at', 'updated_at']
    search_fields = ('title', 'description', 'status', 'creator')