from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','is_active', 'is_superuser', 'is_staff','date_joined')