import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskHistory

User = get_user_model()

@pytest.mark.django_db
class TestTaskAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        response = self.client.post(reverse('token_obtain_pair'), {
            "username": "testuser",
            "password": "testpass"
        })
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_register(self):
        response = self.client.post(reverse('register'), {
            "username": "newuser",
            "password": "newpass123",
            "password2": "newpass123"
        })
        assert response.status_code == 201
        assert User.objects.filter(username="newuser").exists()

    def test_create_task(self):
        response = self.client.post(reverse('task-list'), {
            "name": "Zadanie testowe",
            "description": "Opis zadania",
            "status": "nowy"
        })
        assert response.status_code == 201
        task = Task.objects.get(name="Zadanie testowe")
        assert task.description == "Opis zadania"
        assert TaskHistory.objects.filter(task=task).count() == 4

    def test_update_task(self):
        task = Task.objects.create(name="Zadanie", description="Opis", status="nowy")
        response = self.client.patch(reverse('task-detail', args=[task.id]), {
            "status": "w_toku"
        })
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.status == "w_toku"
        assert TaskHistory.objects.filter(task=task, field="status", old_value="nowy", new_value="w_toku").exists()