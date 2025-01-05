from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import CustomLoginForm
from .forms import RegistrationForm
from .models import Movies, Recommendations, TvShows, Cartoon, Genres, Reviews
from django.core.cache import cache
from django.views.decorators.cache import cache_page


def index(request):
    rec_movies = cache.get('rec_movies')
    model_name = Recommendations.__name__.lower()
    if not rec_movies:
        rec_movies = Recommendations.objects.prefetch_related('genre')
        cache.set('rec_movies', rec_movies, 2592000)  # Кэшируем на 2592000 секунд

    reviews = cache.get('reviews')
    if not reviews:
        reviews = Reviews.objects.prefetch_related('user')
        cache.set('reviews', reviews, 2592000)  # Кэшируем на 2592000 секунд

    return render(request, 'cinema/index.html', context={'movies': rec_movies, 'reviews': reviews,
                                                         'model_name': model_name})


def data_paginator(request, model):
    page_number = request.GET.get('page', 1)
    cache_key = f'{model.__name__}_page_{page_number}'  # Уникальный ключ для кеша на основе модели и страницы

    # Проверка наличия кеша
    page_obj = cache.get(cache_key)

    if not page_obj:
        data = model.objects.prefetch_related('genre')
        paginator = Paginator(data, 25)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        cache.set(cache_key, page_obj, timeout=2592000)

    return page_obj


def movies(request):
    page_obj = data_paginator(request, Movies)
    model_name = Movies.__name__.lower()
    return render(request, 'cinema/movies.html', context={'movies': page_obj.object_list, 'page': page_obj,
                                                          'model_name': model_name})


def tvshows(request):
    page_obj = data_paginator(request, TvShows)
    model_name = TvShows.__name__.lower()
    return render(request, 'cinema/serials.html', context={'movies': page_obj.object_list, 'page': page_obj,
                                                           'model_name': model_name})


def cartoon(request):
    page_obj = data_paginator(request, Cartoon)
    model_name = Cartoon.__name__.lower()
    return render(request, 'cinema/cartoon.html', context={'movies': page_obj.object_list, 'page': page_obj,
                                                           'model_name': model_name})


@cache_page(604800)
def detail(request, model_name, slug):
    models = {
        'movies': Movies,
        'tvshows': TvShows,
        'cartoon': Cartoon,
        'recommendations': Recommendations
    }
    model = models[model_name]
    media = model.objects.get(slug=slug)

    return render(request, 'cinema/detail.html', context={'media': media})


def genre(request):
    # Проверяем, есть ли кешированные данные для жанров
    genres_data = cache.get('genres_data')

    if not genres_data:
        # Получаем все жанры с предварительным выбором нужных данных
        genres = Genres.objects.all()

        # Получаем все фильмы, сериалы и мультфильмы с предварительной загрузкой жанров
        movies = Movies.objects.prefetch_related('genre')
        tv_shows = TvShows.objects.prefetch_related('genre')
        cartoons = Cartoon.objects.prefetch_related('genre')

        # Получаем все фильмы, сериалы и мультфильмы, исключая дублирующиеся постеры
        used_posters = set()  # Храним уже использованные постеры
        genres_data = []

        for genre in genres:
            # Получаем все медиа для жанра и исключаем уже использованные постеры
            genre_movies = movies.filter(genre=genre).exclude(poster_path__in=used_posters)
            genre_tv_shows = tv_shows.filter(genre=genre).exclude(poster_path__in=used_posters)
            genre_cartoons = cartoons.filter(genre=genre).exclude(poster_path__in=used_posters)

            # Объединяем все медиа для жанра в один список
            genre_media = list(genre_movies) + list(genre_tv_shows) + list(genre_cartoons)

            # Ограничиваем до 3 уникальных постеров
            limited_media = []
            for item in genre_media:
                if item.poster_path not in used_posters and len(limited_media) < 3:
                    limited_media.append(item)
                    used_posters.add(item.poster_path)

            # Добавляем данные о жанре и медиа в итоговый список
            genres_data.append({
                'genre': genre,
                'media': limited_media,
            })

        cache.set('genres_data', genres_data, timeout=2592000)
    # Если genres_data пустое, то вернется пустая страница (можно изменить на другую страницу, если нужно)
    return render(request, 'cinema/genre.html', {'genres_data': genres_data})


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')

    else:
        form = RegistrationForm()

    return render(request, 'cinema/registration/register.html', {"form": form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'cinema/registration/login.html'


def logout_view(request):
    logout(request)
