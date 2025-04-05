from django.contrib import admin

# Register your models here.

# http://127.0.0.1:8000/admin/

from .models import Quiz_Question
from .models import Quiz_Choice
from .models import Quiz_User

admin.site.register(Quiz_Question)
admin.site.register(Quiz_Choice)
admin.site.register(Quiz_User)
