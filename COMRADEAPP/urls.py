from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile_setup/', views.profile_setup, name='profile_setup'),
    path('add_income/', views.add_income, name='add_income'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('delete_expense/<int:pk>', views.delete_expense, name='delete_expense'),
    path('category_setup/', views.category_setup, name='category_setup'),
    path('add_category/', views.add_category, name='add_category'),
    path('summary/', views.summary_view, name='summary'),
]


