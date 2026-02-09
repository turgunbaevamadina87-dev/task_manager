from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from datetime import datetime
from rest_framework import viewsets, permissions
from .pagination import TaskPagination
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import TaskSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Task


class TaskViewSet(viewsets.ModelViewSet):
    """
    /api/tasks/
    /api/tasks/{id}/
    """
    pagination_class = TaskPagination
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "deadline"]
    search_fields = ["title"]
    ordering_fields = ["created_at"]

    # Показываем только задачи пользователя
def get_queryset(self):
    return Task.objects.filter(owner=self.request.user)

    # Автоматически назначаем owner
def perform_create(self, serializer):
    serializer.save(owner=self.request.user)



# Главная страница — список задач
@login_required(login_url="/users/login/")
def task_list(request):
    tasks = Task.objects.filter(owner=request.user)
    return render(request, "tasks.html", {"tasks": tasks})

# Добавление задачи

@login_required(login_url="/users/login/")
def task_add(request):
    error = None
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status")
        deadline_str = request.POST.get("deadline", "").strip()

        # Проверка названия
        if not title:
            error = "Название задачи не может быть пустым"

        # Проверка описания
        elif len(description) < 10:
            error = "Описание должно быть минимум 10 символов"

        # Проверка даты
        elif not deadline_str:
            error = "Дедлайн обязателен"
        else:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            except ValueError:
                error = "Неверный формат даты. Используйте YYYY-MM-DD."
            else:
                # Проверка, что дата не в прошлом
                if deadline < timezone.now().date():
                    error = "Дата не может быть в прошлом!"
                else:
                    # Всё верно, создаём задачу
                    Task.objects.create(
                        title=title,
                        description=description,
                        status=status,
                        deadline=deadline,
                        owner=request.user
                    )
                    return redirect("task_list")

    # Передаём текущую дату для min в HTML
    today = timezone.now().date()

    return render(request, "task_add.html", {"error": error, "today": today})

# Редактирование задачи
@login_required(login_url="/users/login/")
def task_edit(request, id):
    task = get_object_or_404(Task, id=id, owner=request.user)
    if request.method == "POST":
        task.title = request.POST.get("title")
        task.description = request.POST.get("description")
        task.status = request.POST.get("status")
        task.deadline = request.POST.get("deadline")
        task.save()
        return redirect("task_list")
    return render(request, "task_edit.html", {"task": task})


@login_required
def task_list(request):
    tasks = Task.objects.filter(owner=request.user)

    # ---------- ФИЛЬТРЫ ----------
    status = request.GET.get("status")
    deadline = request.GET.get("deadline")
    search = request.GET.get("search")

    if status:
        tasks = tasks.filter(status=status)

    if deadline:
        tasks = tasks.filter(deadline=deadline)

    if search:
        tasks = tasks.filter(title__icontains=search)

    # ---------- СОРТИРОВКА ----------
    ordering = request.GET.get("ordering", "-created_at")
    tasks = tasks.order_by(ordering)

    # ---------- СТАТИСТИКА ----------
    stats = {
        "todo": tasks.filter(status="todo").count(),
        "progress": tasks.filter(status="in_progress").count(),
        "done": tasks.filter(status="done").count(),
        "total": tasks.count(),
    }

    # ---------- ПАГИНАЦИЯ ----------
    paginator = Paginator(tasks, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "tasks.html", {
        "tasks": page_obj,
        "page_obj": page_obj,
        "stats": stats,
    })

@login_required
def home_view(request):
    return render(request, "tasks.html")

# Перемещение задачи (todo / in_progress / done)
@login_required
def move_task(request, pk, status):
    task = get_object_or_404(Task, pk=pk, owner=request.user)

    # Логика перехода только вперёд
    if task.status == 'todo' and status == 'in_progress':
        task.status = 'in_progress'
    elif task.status == 'in_progress' and status == 'done':
        task.status = 'done'

    task.save()
    return redirect('tasks:task_list')



def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password_confirm = request.POST["password_confirm"]

        # пароль не совпадает
        if password != password_confirm:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        # 🚨 ВАЖНО — проверка username
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        # создаём пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")  # или "home"

    return render(request, "register.html")



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 👇 МАГИЯ ТУТ
    filter_backends = [
        DjangoFilterBackend,   # фильтрация
        filters.SearchFilter,  # поиск
        filters.OrderingFilter # сортировка
    ]

    # Фильтрация
    filterset_fields = ["status", "deadline"]

    # Поиск
    search_fields = ["title"]

    # Сортировка
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]  # по умолчанию новые сверху

    # показываем только задачи текущего пользователя
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

@api_view(["GET"])
def task_stats(request):
    user = request.user

    total = Task.objects.filter(owner=user).count()
    done = Task.objects.filter(owner=user, status="done").count()
    pending = Task.objects.filter(owner=user, status="pending").count()

    return Response({
        "total": total,
        "done": done,
        "pending": pending
    })

@login_required
def task_move(request, pk, status):  # pk и status приходят из URL
    task = get_object_or_404(Task, pk=pk, owner=request.user)

    # Смена статуса
    if task.status == 'todo' and status == 'in_progress':
        task.status = 'in_progress'
        task.save()
    elif task.status == 'in_progress' and status == 'done':
        task.status = 'done'
        task.save()
    # можно добавить другие проверки

    return redirect("task_list")




