from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from multiselectfield import MultiSelectField

from concert.models import *


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('email is required')
        user = self.model(
                email=self.normalize_email(email),
                username=username
                )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
                email=self.normalize_email(email),
                username=username,
                password=password
                )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    # 필수 정보 (이메일, 아이디)
    email = models.EmailField(
            max_length=255,
            unique=True,
            )
    username = models.CharField(
            max_length=31,
            null=False,
            unique=True,
            )

    # 개인화에 이용되는 정보 (선호장르, 거주지역)
    preferred_genres = MultiSelectField(
            verbose_name='User Preffered Genres',
            choices=GENRES,
            null=True,
            )
    region = models.CharField(
            verbose_name='User Address Region',
            choices=REGIONS,
            max_length=15,
            null=True,
            )
    
    # 북마크 정보 (콘서트, 가수)
    concerts = models.ManyToManyField(
            verbose_name='Bookmarked Concerts',
            to=Concert,
            )
    artists = models.ManyToManyField(
            verbose_name='Bookmarked Artists',
            to=Artist,
            )

    # 관리 정보
    is_active = models.BooleanField(
            default=True,
            )
    is_admin = models.BooleanField(
            default=False,
            )
    is_superuser = models.BooleanField(
            default=False,
            )
    is_staff = models.BooleanField(
            default=False,
            )
    date_joined = models.DateTimeField(
            auto_now_add=True,
            )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

