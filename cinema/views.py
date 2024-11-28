from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import CustomLoginForm
from .forms import RegistrationForm
from .models import Movies, Recommendations, TvShows


def index(request):
    rec_movies = Recommendations.objects.all()

    return render(request, 'cinema/index.html', context={'movies': rec_movies})


def movies(request):
    data = Movies.objects.all()

    paginator = Paginator(data, 25)  # 25 записей на страницу
    page_number = request.GET.get("page", 1)  # Определение текущей страницы

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)  # Если `page` не является числом, вернуть первую страницу
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # Если страница вне диапазона, вернуть последнюю страницу

    return render(request, 'cinema/movies.html', context={'movies': page_obj.object_list, 'page': page_obj})


def serials(request):
    data = TvShows.objects.all()

    paginator = Paginator(data, 25)  # 25 записей на страницу
    page_number = request.GET.get("page", 1)  # Определение текущей страницы

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)  # Если `page` не является числом, вернуть первую страницу
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # Если страница вне диапазона, вернуть последнюю страницу

    return render(request, 'cinema/serials.html', context={'movies': page_obj.object_list, 'page': page_obj})


def genre(request):
    return render(request, 'cinema/genre.html')


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')

    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {"form": form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm


def logout_view(request):
    logout(request)
