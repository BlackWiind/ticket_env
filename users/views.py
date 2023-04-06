from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .form import RegisterCostumerForm


def register_custumer(request):
    if request.method == 'POST':
        form = RegisterCostumerForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_customer = True
            user.save()
            messages.info(request, 'Пользователь успешно зарегестрирован.')
            return redirect('login')
        else:
            messages.warning(request, 'Что-то пошло не так. Проверьте введённую информацию.')
            return redirect('register-customer')
    else:
        form = RegisterCostumerForm()
        context = {'form':form}
        return render(request, 'user/register_customer.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            messages.info(request, 'Вход успешен')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Что-то пошло не так. Проверьте ввудённые данные.')
            return redirect('login')
    else:
        return render(request, 'users/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'Войдите, что-бы продолжить')
    return redirect('login')
