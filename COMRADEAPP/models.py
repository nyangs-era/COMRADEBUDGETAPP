from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    UNIVERSITY_CHOICES = [
        ('public', 'Public University'),
        ('private', 'Private University'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university_type = models.CharField(max_length=10, choices=UNIVERSITY_CHOICES)
    semester_duration = models.IntegerField(help_text="Semester duration in months")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.user.username

class Income(models.Model):

    SOURCE_CHOICES = [
        ('helb', 'HELB'),
        ('pocket_money', 'Pocket Money'),
        ('side_hustle', 'Side Hustle'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.source}"
class Category(models.Model):

    CATEGORY_TYPE = [
        ('essential', 'Essential'),
        ('lifestyle', 'Lifestyle'),
        ('optional', 'Optional'),
        ('savings', 'Savings'),
    ]

    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE)

    def __str__(self):
        return self.name
class Budget(models.Model):

    BUDGET_LEVEL = [
        ('low', 'Low Budget Comrade'),
        ('medium', 'Medium Budget Comrade'),
        ('high', 'High Budget Comrade'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_level = models.CharField(max_length=10, choices=BUDGET_LEVEL)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
class Expense(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
