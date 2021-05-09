from django.contrib import admin
from .models import sensors

# Register your models here.

admin.site.site_header = "DBoT Admin"
admin.site.site_title = "DBoT Admin Area"
admin.site.index_header = "Welcome to the DBoT admin area"

admin.site.register(sensors)
