from django.urls import path
from accounts import views

urlpatterns = [
    path('signup/', views.UserRegisterView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]