from django.contrib import admin

# Register your models here.

# http://127.0.0.1:8000/admin/

from .models import Quiz_Question, Quiz_Choice, Quiz_User, Quiz_Response

admin.site.register(Quiz_Question)
admin.site.register(Quiz_Choice)
admin.site.register(Quiz_Response)

class UserAdmin(admin.ModelAdmin):
    readonly_fields=('created_at',)

admin.site.register(Quiz_User, UserAdmin)