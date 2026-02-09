from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, task_add, task_edit,  move_task,task_stats
from django.contrib.auth import views as auth_views
from .views import task_move, task_list
router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="tasks")

app_name = "tasks"

urlpatterns = [
    # 🔥 главная страница
    path("", task_list, name="task_list"),

    # API
    path("api/", include(router.urls)),

    # HTML
    path("add/", task_add, name="task_add"),
    path("tasks/<int:id>/edit/", task_edit, name="task_edit"),
    path("<int:pk>/move/<str:status>/", move_task, name="move_task"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("stats/", task_stats),
    path("<int:pk>/move/<str:status>/", task_move, name="task_move"),
    path("", task_list, name="task_list"),
]