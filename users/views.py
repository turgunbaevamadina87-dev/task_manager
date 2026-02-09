from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect("login")



def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        # 1️⃣ Проверка на пустые поля
        if not username or not email or not password or not password_confirm:
            return render(request, "register.html", {"error": "Заполните все поля"})

        # 2️⃣ Проверка уникальности username
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Пользователь с таким именем уже существует"})

        # 3️⃣ Проверка уникальности email
        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Пользователь с таким email уже существует"})

        # 4️⃣ Проверка длины пароля
        if len(password) < 8:
            return render(request, "register.html", {"error": "Пароль должен содержать минимум 8 символов"})

        # 5️⃣ Проверка совпадения паролей
        if password != password_confirm:
            return render(request, "register.html", {"error": "Пароли не совпадают"})


        user = User.objects.create_user(username=username, email=email, password=password)
        return redirect("login")  # редирект на страницу логина

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("task_list")# <- важно, куда редиректим
        else:
            error = "Неправильные данные"
            return render(request, "login.html", {"error": error})
    return render(request, "login.html")


# API Register
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]