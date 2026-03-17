from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RegisterForm, ProfileForm, IncomeForm, ExpenseForm
from .models import Income, Expense, Category, Profile


# -----------------------------------------
# USER REGISTRATION
# -----------------------------------------
def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('profile_setup')
    return render(request, 'register.html', {'form': form})


# -----------------------------------------
# LOGIN
# -----------------------------------------
def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'login.html', {'form': form})


# -----------------------------------------
# LOGOUT
# -----------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# -----------------------------------------
# PROFILE SETUP
# -----------------------------------------
@login_required
def profile_setup(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'profile_setup.html', {'form': form})


# -----------------------------------------
# BUDGET ALLOCATION LOGIC
# -----------------------------------------
def calculate_budget(user):
    profile = Profile.objects.get(user=user)
    incomes = Income.objects.filter(user=user)
    total_income = sum(i.amount for i in incomes)
    categories = Category.objects.all()
    allocations = {}
    for category in categories:
        allocations[category.name] = (category.percentage / 100) * total_income
    return allocations


# -----------------------------------------
# SEMESTER BUDGET CALCULATOR
# -----------------------------------------
def semester_budget(user):
    profile = Profile.objects.get(user=user)
    incomes = Income.objects.filter(user=user)
    total_income = sum(i.amount for i in incomes)
    weeks = profile.semester_duration
    if weeks == 0:
        return 0
    weekly_budget = total_income / weeks
    return round(weekly_budget, 2)


# -----------------------------------------
# DASHBOARD
# -----------------------------------------
@login_required
def dashboard(request):
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    balance = total_income - total_expense

    weekly_budget = semester_budget(request.user)
    allocations = calculate_budget(request.user)

    category_spending = {}
    for expense in expenses:
        name = expense.category.name
        if name not in category_spending:
            category_spending[name] = 0
        category_spending[name] += float(expense.amount)

    alerts = []
    for category, spent in category_spending.items():
        if category in allocations and spent > allocations[category]:
            alerts.append(f"You overspent in {category}")

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'weekly_budget': weekly_budget,
        'expenses': expenses,
        'alerts': alerts
    }

    return render(request, 'dashboard.html', context)


# -----------------------------------------
# ADD INCOME
# -----------------------------------------
@login_required
def add_income(request):
    form = IncomeForm(request.POST or None)
    if form.is_valid():
        income = form.save(commit=False)
        income.user = request.user
        income.save()
        return redirect('dashboard')
    return render(request, 'add_income.html', {'form': form})


# -----------------------------------------
# ADD EXPENSE
# -----------------------------------------
@login_required
def add_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        return redirect('dashboard')
    return render(request, 'add_expense.html', {'form': form})

