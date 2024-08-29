from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

class Application(models.Model):
    application_name = models.CharField(max_length=255, unique=True)
    application_address = models.TextField()
    is_ats = models.IntegerField()
    application_mobileno = models.CharField(max_length=100)
    license_start_date = models.DateField(auto_now_add=True)
    license_end_date = models.DateField()
    no_of_license = models.IntegerField(default=1)
    website = models.CharField(max_length=255)
    application_pan_no = models.CharField(max_length=150)
    application_gst_no = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    default_status_id = models.IntegerField()
    default_referrer_id = models.IntegerField()
    secret_key = models.CharField(max_length=255)
    term_and_condition = models.BooleanField(default=False)
    state_name = models.CharField(max_length=150)
    logo_url = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    can_call = models.BooleanField(default=False)
    disable_crowed_sourcing = models.BooleanField(default=False)
    application_about = models.TextField()
    call_port_allow = models.IntegerField(default=2)
    working_days = models.IntegerField(default=5)
    billing_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'applications'
class UserManager(BaseUserManager):
    def create_user(self, email, username, name, application_id, first_name, last_name, password=None, **extra_fields):
        user = self.model(email=self.normalize_email(email), username=username, name=name, application_id=application_id, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, phone, password=None):
        user = self.create_user(email=email, username=username, password=password, first_name=first_name, last_name=last_name, phone=phone)
        user.is_admin = True
        user.is_staff = True
        user.name = f'{first_name} {last_name}'
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    uid = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
    role_id = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, default='.')
    username = models.CharField(max_length=100)
    phone = models.CharField(max_length=12, unique=True, null=True)
    date_joined = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    gender = models.IntegerField(null=True)
    profile_pic = models.CharField(max_length=150, null=True, blank=True)
    mobile_no = models.CharField(max_length=150, unique=True, default='1')
    dob = models.DateField(default='2022-08-12')
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    manager = models.IntegerField(null=True, blank=True)
    short_name = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    login_attempts = models.IntegerField(default=0)
    forget_password_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'mobile_no', 'name']
    password = models.CharField(max_length=1024)
    objects = UserManager()

    def __str__(self):
        return self.email + ", " + self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    class Meta:
        managed = False
        db_table = 'users'
