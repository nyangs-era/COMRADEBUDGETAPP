from django.contrib import admin
from .models import Profile, Income, Category, Budget, Expense

admin.site.register(Profile)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(Budget)
admin.site.register(Expense)