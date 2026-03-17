from django import forms
from django.contrib.auth.models import User
from .models import Profile,Income,Expense


# User registration form
class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:

        model = User

        fields = ['username','email','password']



# Profile setup form
class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = ['university_type','semester_duration','gender','budget_level']

# Income form
class IncomeForm(forms.ModelForm):

    class Meta:

        model = Income

        fields = ['source','amount']



# Expense form
class ExpenseForm(forms.ModelForm):

    class Meta:

        model = Expense

        fields = ['category','amount']