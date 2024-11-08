from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import CustomLoginForm
from .forms import RegistrationForm


def index(request):
    return render(request, 'cinema/index.html')


def movies(request):
    return render(request, 'cinema/movies.html')


def serials(request):
    return render(request, 'cinema/serials.html')


def genre(request):
    return render(request, 'cinema/genre.html')


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')

        # 4 - Забыли пароль оформить !
        # 7 - Перезагрзку страницы для полей и ошибок
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {"form": form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm


def logout_view(request):
    logout(request)

