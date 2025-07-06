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

    def test_create_task_without_description(self):
        response = self.client.post(reverse('task-list'), {
            "name": "Task without description",
            "status": "nowy"
        })
        assert response.status_code == 201
        task = Task.objects.get(name="Task without description")
        assert not task.description

    def test_create_task_with_assigned_user(self):
        another_user = User.objects.create_user(username="assigneduser", password="pass123")
        response = self.client.post(reverse('task-list'), {
            "name": "Task with user",
            "status": "nowy",
            "assigned_to": another_user.id
        })
        assert response.status_code == 201
        task = Task.objects.get(name="Task with user")
        assert task.assigned_to == another_user

    def test_list_tasks_filter_by_status(self):
        Task.objects.create(name="Task1", status="nowy")
        Task.objects.create(name="Task2", status="w_toku")
        response = self.client.get(reverse('task-list'), {"status": "nowy"})
        assert response.status_code == 200
        assert any(task["name"] == "Task1" for task in response.data)
        assert all(task["status"] == "nowy" for task in response.data)

    def test_search_tasks_by_name(self):
        Task.objects.create(name="Cooking dinner", status="nowy")
        Task.objects.create(name="Shopping", status="nowy")
        response = self.client.get(reverse('task-list'), {"search": "cook"})
        assert response.status_code == 200
        assert any("Cooking" in task["name"] for task in response.data)

    def test_delete_task(self):
        task = Task.objects.create(name="Delete me", status="nowy")
        response = self.client.delete(reverse('task-detail', args=[task.id]))
        assert response.status_code == 204
        assert not Task.objects.filter(id=task.id).exists()

    def test_task_history_filter_by_task(self):
        task = Task.objects.create(name="History test", status="nowy")
        task.status = "w_toku"
        task.save()
        response = self.client.get(reverse('taskhistory-list'), {"task": task.id})
        assert response.status_code == 200
        assert all(hist["task"] == task.id for hist in response.data)

    def test_cannot_create_task_without_name(self):
        response = self.client.post(reverse('task-list'), {
            "description": "No name"
        })
        assert response.status_code == 400
        assert "name" in response.data

    def test_update_task_assigned_user(self):
        task = Task.objects.create(name="Assign user", status="nowy")
        user2 = User.objects.create_user(username="user2", password="pass2")
        response = self.client.patch(reverse('task-detail', args=[task.id]), {
            "assigned_to": user2.id
        })
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.assigned_to == user2

    def test_get_task_detail(self):
        task = Task.objects.create(name="Detail task", status="nowy")
        response = self.client.get(reverse('task-detail', args=[task.id]))
        assert response.status_code == 200
        assert response.data["name"] == "Detail task"

    def test_register_with_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            "username": "userbadpass",
            "password": "pass1",
            "password2": "pass2"
        })
        assert response.status_code == 400
        assert "non_field_errors" in response.data
