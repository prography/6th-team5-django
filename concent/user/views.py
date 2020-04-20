from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import User
from .serializers import UserSerializer


class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer