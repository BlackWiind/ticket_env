from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterCostumerForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'department',]