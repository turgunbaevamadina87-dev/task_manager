from rest_framework import serializers
from datetime import date
from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["owner", "created_at", "updated_at"]

    # 🔹 title
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    # 🔹 description
    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters")
        return value

    # 🔹 deadline
    def validate_deadline(self, value):
        if value < date.today():
            raise serializers.ValidationError("Deadline cannot be in the past")
        return value

    # 🔹 общая проверка (если понадобится)
    def validate(self, data):
        return data