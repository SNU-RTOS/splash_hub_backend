from django.contrib import admin

from .models import *

admin.site.register(Project)
admin.site.register(Code) 
admin.site.register(CustomMessage)
admin.site.register(MessageField)