"""Account-related models."""

from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
	"""Custom manager where email is the unique identifiers."""

	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError(_('The email address must be set'))
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))

		return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
	"""Application custom user identified by email."""

	username = None
	uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
	email = models.EmailField(_('adresse e-mail'), unique=True)
	phone_number = models.CharField(_('téléphone'), max_length=30, blank=True)
	organisation = models.CharField(_('organisation'), max_length=255, blank=True)
	title = models.CharField(_('fonction'), max_length=120, blank=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = UserManager()

	class Meta:
		ordering = ('email',)
		verbose_name = _('utilisateur')
		verbose_name_plural = _('utilisateurs')

	def __str__(self):
		return self.email
