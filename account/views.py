from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from account.forms import *
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
# Create your views here.


def register(request):
    user = request.user
    if user.is_authenticated:
        return redirect("home")
    context = {}
    show = False
    if request.POST:
        form_type = request.POST["form_type"]
        if form_type == "login":
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                data = login_form.cleaned_data
                username = data["username"]
                password = data["password"]
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect("home")

            register_form = RegistrationForm()

        elif form_type == "register":
            register_form = RegistrationForm(request.POST)

            if register_form.is_valid():
                register_form.save()
                username = request.POST["username"]
                password = request.POST["password1"]
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect("home")
            show = True
            login_form = LoginForm()

    else:
        login_form = LoginForm()
        register_form = RegistrationForm()
    context["registration_form"] = register_form
    context["login_form"] = login_form
    context["show"] = show
    return render(request, "account/register.html", context)


def logout_(request):
    logout(request)
    return redirect("register")
