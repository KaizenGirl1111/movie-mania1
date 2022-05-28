from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from accounts.forms import UserForm


# Create your views here.
# Register user
class UserRegisterView(CreateView):
    form_class = UserForm
    template_name = 'signUp.html'
    success_url = reverse_lazy('movies:index')

    def form_valid(self, form):
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)


# Login User
class LoginView(TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if not user:
            return render(request, 'login.html', {'error_message': 'Invalid Login'})

        if not user.is_active:
            return render(request, 'login.html', {'error_message': 'Your account disable'})

        login(request, user)
        return redirect("movies:index")


# Logout user
def logout_view(request):
    logout(request)
    return redirect("login")
