

from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskHistoryViewSet
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView


router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'task-history', TaskHistoryViewSet, basename='taskhistory')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls