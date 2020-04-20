from . import views
from django.urls import path

urlpatterns = [
    path('user/', views.UserList.as_view(), name='user_list'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user_detail')
]