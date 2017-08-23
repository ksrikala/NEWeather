from django.contrib import admin

from necloudweather.models import *

admin.site.register(azure_americas)
admin.site.register(azure_asia)
admin.site.register(azure_europe)
admin.site.register(aws_na)
admin.site.register(aws_sa)
admin.site.register(aws_ap)
admin.site.register(aws_eu)

# Register your models here.
