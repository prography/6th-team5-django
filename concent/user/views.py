from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.contrib.auth.models import User
from .serializers import UserSerializer

# Create your views here.


class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer