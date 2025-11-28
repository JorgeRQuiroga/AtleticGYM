from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from .forms import LoginForm


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm


def error_403(request, exception=None):
    return render(request, '403.html', status=403)
