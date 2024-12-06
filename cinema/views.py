from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import CustomLoginForm
from .forms import RegistrationForm
from .models import Movies, Recommendations, TvShows, Cartoon, Genres, Reviews


def index(request):
    rec_movies = Recommendations.objects.all()
    reviews = Reviews.objects.all()

    return render(request, 'cinema/index.html', context={'movies': rec_movies, 'reviews': reviews})


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


# Сделать страницу Мультфильмы!!!
# Страницу Жанров !!!
# Адаптация всех страниц навигации
# Сделать наводку на ссылку фильмы правильную !!!
# Уменьшения кода в utils, и во вьюхе повторяющий код в функциях


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
    genres = Genres.objects.all()
    used_posters = set()  # Храним уже использованные постеры
    genres_data = []

    for genre in genres:
        # Получаем медиа для текущего жанра
        movies = Movies.objects.filter(genre=genre).exclude(poster_path__in=used_posters)
        tv_shows = TvShows.objects.filter(genre=genre).exclude(poster_path__in=used_posters)
        cartoons = Cartoon.objects.filter(genre=genre).exclude(poster_path__in=used_posters)

        # Объединяем данные из всех моделей
        media = list(movies) + list(tv_shows) + list(cartoons)

        # Ограничиваем до 3 уникальных постеров
        media = [item for item in media if item.poster_path not in used_posters][:3]

        # Обновляем список использованных постеров
        used_posters.update(item.poster_path for item in media)

        # Добавляем жанр и связанные медиа в список данных
        genres_data.append({
            'genre': genre,
            'media': media,
        })

    # Если genres_data пустое, то вернется пустая страница (можно изменить на другую страницу, если нужно)
    return render(request, 'cinema/genre.html', {'genres_data': genres_data})


def cartoon(request):
    data = Cartoon.objects.all()

    paginator = Paginator(data, 25)  # 25 записей на страницу
    page_number = request.GET.get("page", 1)  # Определение текущей страницы

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)  # Если `page` не является числом, вернуть первую страницу
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # Если страница вне диапазона, вернуть последнюю страницу

    return render(request, 'cinema/cartoon.html', context={'movies': page_obj.object_list, 'page': page_obj})


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
