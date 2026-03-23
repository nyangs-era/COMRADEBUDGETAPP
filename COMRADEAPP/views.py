from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RegisterForm, ProfileForm, IncomeForm, ExpenseForm
from .models import Income, Expense, Category, Profile, DEFAULT_CATEGORIES

from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

import json

# -----------------------------------------
# USER REGISTRATION
# -----------------------------------------

def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        Profile.objects.create(user=user)

        # 🔥 create default categories
        for name, percent, icon in DEFAULT_CATEGORIES:
            Category.objects.create(
                user=user,
                name=name,
                suggested_percentage=percent,
                icon=icon
            )

        login(request, user)
        return redirect('profile_setup')

    return render(request, 'COMRADEAPP/register.html', {'form': form})

# -----------------------------------------
# LOGIN
# -----------------------------------------
def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'COMRADEAPP/login.html', {'form': form})


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
    profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)

    if request.method == 'POST':
        semester_start = request.POST.get('semester_start')
        semester_end = request.POST.get('semester_end')

        profile.semester_start = semester_start
        profile.semester_end = semester_end
        
    if form.is_valid():
        form.save()
        return redirect('add_income')
    return render(request, 'COMRADEAPP/profile_setup.html', {'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon')

        Category.objects.create(
            user=request.user,
            name=name,
            suggested_percentage=0,
            icon=icon
        )
        return redirect('category_setup')

    return render(request, 'COMRADEAPP/add_category.html')

# -----------------------------------------
# BUDGET ALLOCATION LOGIC
# -----------------------------------------

def calculate_budget(user):
    categories = Category.objects.filter(user=user, is_selected=True)
    allocations = {}

    for category in categories:
        percent = category.custom_percentage or category.suggested_percentage
        allocations[category.name] = percent

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
    user = request.user

    # CATEGORY TOTALS (for pie chart)
    category_data = (
        Expense.objects
        .filter(user=user)
        .values('category__name')
        .annotate(total=Sum('amount'))
    )

    categories = [item['category__name'] for item in category_data]
    totals = [float(item['total']) for item in category_data]

    # LAST 7 DAYS (bar chart)
    last_7_days = now() - timedelta(days=7)

    daily_data = (
        Expense.objects
        .filter(user=user, date__gte=last_7_days)
        .extra(select={'day': "date(date)"})
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    days = [str(item['day']) for item in daily_data]
    daily_totals = [float(item['total']) for item in daily_data]

    # 🔹 Add total spending to avoid template sum filter
    total_spending = sum(totals)

    # prevent blank charts
    if not categories:
        categories = ['No Data']
        totals = [0]

    if not days:
        days = ['No Data']
        daily_totals = [0]

    context = {
    'categories': json.dumps(categories),
    'totals': json.dumps(totals),
    'days': json.dumps(days),
    'daily_totals': json.dumps(daily_totals),
    'total_spending': total_spending,  # <-- pass sum here
    }

    return render(request, 'COMRADEAPP/dashboard.html', context)

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
        return redirect('category_setup')
    return render(request, 'COMRADEAPP/add_income.html', {'form': form})


# -----------------------------------------
# ADD EXPENSE
# -----------------------------------------
@login_required
def add_expense(request):
    categories = Category.objects.filter(user=request.user, is_selected=True)

    if request.method == "POST":
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')

        selected_category = Category.objects.get(id=category_id, user=request.user)

        Expense.objects.create(
            user=request.user,
            category=selected_category, 
            amount=amount
        )

        return redirect('dashboard')

    return render(request, 'COMRADEAPP/add_expense.html', {
        'categories': categories
    })

def delete_expense(request,pk):
    expense = Expense.objects.get(id=pk, user=request.user)
    expense.delete()
    return redirect('dashboard')

@login_required
def category_setup(request):
    categories = Category.objects.filter(user=request.user)
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    if request.method == "POST":
        for cat in categories:
            # toggle
            cat.is_selected = request.POST.get(f"cat_{cat.id}") == "on"

            # slider value
            percent = request.POST.get(f"percent_{cat.id}")
            if percent:
                cat.custom_percentage = float(percent)

            cat.save()

        return redirect('dashboard')

    return render(request, 'COMRADEAPP/category_setup.html', {
    'categories': categories,
    'total_income': total_income
})

def calculate_allocation(income):
    return {
        "Food": income * 0.3,
        "Rent": income * 0.4,
        "Transport": income * 0.1,
    }


@login_required
def summary_view(request):
    # --- EXISTING DATA ---
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    remaining = total_income - total_spent

    # --- WEEKLY BUDGET (SAFE INTEGRATION) ---
    weekly_budget = 0
    weeks_left = 0

    try:
        profile = request.user.profile

        if profile.semester_start and profile.semester_end:
            today = now().date()

            days_left = (profile.semester_end - today).days
            weeks_left = max(days_left / 7, 1)

            weekly_budget = remaining / weeks_left if weeks_left > 0 else 0

    except:
        # prevents crash if profile doesn't exist yet
        pass

    # --- CATEGORY SUMMARY ---
    category_summary = expenses.values('category__name').annotate(
        total=Sum('amount')
    )

    context = {
        'total_income': total_income,
        'total_spent': total_spent,
        'remaining': remaining,
        'weekly_budget': weekly_budget,
        'weeks_left': weeks_left,
        'category_summary': category_summary,
    }

    return render(request, 'COMRADEAPP/summary.html', context)
