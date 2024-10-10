from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        self._validate_create_superuser_method(password, **extra_fields)
        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        self._validate__create_user_method(email, **extra_fields)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else: user.set_unusable_password()
        user.save(using=self._db)
        return user

    @staticmethod
    def _validate__create_user_method(email, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

    @staticmethod
    def _validate_create_superuser_method(password, **extra_fields):
        if password is None:
            raise ValueError("The password must be set")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
