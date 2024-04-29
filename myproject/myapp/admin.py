from django.contrib import admin
from .models import Bus, User, Book,City

# Register your models here.

admin.site.register(Bus)
admin.site.register(User)
admin.site.register(Book)
admin.site.register(City)