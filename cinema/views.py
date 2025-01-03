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


def data_paginator(request, model):
    data = model.objects.all()

    paginator = Paginator(data, 25)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


def movies(request):
    page_obj = data_paginator(request, Movies)

    return render(request, 'cinema/movies.html', context={'movies': page_obj.object_list, 'page': page_obj})


def serials(request):
    page_obj = data_paginator(request, TvShows)

    return render(request, 'cinema/serials.html', context={'movies': page_obj.object_list, 'page': page_obj})


def cartoon(request):
    page_obj = data_paginator(request, Cartoon)

    return render(request, 'cinema/cartoon.html', context={'movies': page_obj.object_list, 'page': page_obj})


def detail_move(request, slug):
    media = Movies.objects.get(slug=slug)

    return render(request, 'cinema/detail.html', context={'media': media})


def detail_recommendations(request, slug):
    media = Recommendations.objects.get(slug=slug)

    return render(request, 'cinema/detail.html', context={'media': media})


def detail(request, slug):
    media = Cartoon.objects.get(slug=slug)

    return render(request, 'cinema/detail.html', context={'media': media})


def detail_serials(request, slug):
    media = TvShows.objects.get(slug=slug)

    return render(request, 'cinema/detail.html', context={'media': media})

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
