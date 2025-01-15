import asyncio

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from hdrezka import Search

from .forms import CustomLoginForm
from .forms import RegistrationForm
from .models import Movies, Recommendations, TvShows, Cartoon, Genres, Reviews


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
    # cache_key = f'{model.__name__}_page_{page_number}'  # Уникальный ключ для кеша на основе модели и страницы

    # Проверка наличия кеша
    # page_obj = cache.get(cache_key)

    if True:  # not #page_obj:
        data = model.objects.prefetch_related('genre')
        paginator = Paginator(data, 25)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # cache.set(cache_key, page_obj, timeout=2592000)

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


class BaseSearchResultView(ListView):
    template_name = 'cinema/search.html'
    model = None

    def get_queryset(self):
        if self.model is None:
            return f'model name is {self.model.__name__.lower()}'
        query = self.request.GET.get('q', '')

        return self.model.objects.filter(
            Q(title__icontains=query) | Q(title_en__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        if not self.model:
            context['page'] = []
            context['object_list'] = []
            return context
        object_list = self.model.objects.filter(
            Q(title__icontains=query) | Q(title_en__icontains=query)
        )
        paginator = Paginator(object_list, 25)
        page_number = self.request.GET.get('page', 1)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context['page'] = page_obj
        context['object_list'] = object_list
        context['model_name'] = self.model.__name__.lower()

        return context


class SearchResultsMovieView(BaseSearchResultView):
    model = Movies


class SearchResultsTvShowsView(BaseSearchResultView):
    model = TvShows


class SearchResultsCartoonView(BaseSearchResultView):
    model = Cartoon


# Асинхронная функция для загрузки данных о плеере
async def get_player_data(slug, model_name, year, season, episode):
    # Поиск по слагу
    try:
        search_results = await Search(slug).get_page(1)
        print(search_results)
        if not search_results:
            return None

        first_result = None

        # Поиск по году
        for result in search_results:
            # Разделяем строку info по запятой и пробелу
            year_range = result.info.split(', ')[0]

            # Если год — это диапазон, разделим его по '-'
            if '-' in year_range:
                start_year = year_range.split('-')[0]
            else:
                # Если это просто год, используем его как start_year
                start_year = year_range

            # Сравниваем start_year с переданным годом
            if str(start_year) == str(year):
                print(f"Year found: {year} ======= {start_year}")
                print(result)
                first_result = result
                break

        if first_result is None:
            return None  # Возвращаем None, если не нашли год

        print(first_result)

        player = await first_result.player

        # Поиск переводчика с субтитрами
        translator_id = None
        for name, id_ in player.post.translators.name_id.items():
            if 'субтитры' in name.casefold():
                translator_id = id_
                break
        print(f' translator_id - {translator_id}')

        # Получение потока видео
        if model_name == 'tvshows':
            available_seasons = await player.get_episodes(translator_id)

            if season and episode:
                stream = await player.get_stream(int(season), int(episode), translator_id)
            else:
                stream = await player.get_stream(1, 1, translator_id)

            available_seasons_list = list(available_seasons.items())

        else:
            stream = await player.get_stream(translator_id)
            available_seasons_list = None

        print(stream.video)

        print(stream.subtitles.subtitle_names)

        subtitles_urls = {
            'english_sub': stream.subtitles.subtitle_names.get('English').url if stream.subtitles.subtitle_names.get(
                'English') else None,
            'russian_sub': stream.subtitles.subtitle_names.get('Русский').url if stream.subtitles.subtitle_names.get(
                'Русский') else None
        }

        video_urls = {
            'best_quality': await stream.video.last_url,
            'url_360p': stream.video[360].raw_data.get('360p'),
            'url_480p': stream.video[480].raw_data.get('480p'),
            'url_720p': stream.video[720].raw_data.get('720p'),
            'url_1080p': stream.video[1080].raw_data.get('1080p'),
            'url_1080p_Ultra': stream.video[1080]['ultra'].raw_data.get('1080p Ultra'),
        }

        return {
            'video_urls': video_urls,
            'subtitles_url': subtitles_urls,
            'available_seasons_list': available_seasons_list,
        }

    except TimeoutError:
        # Обработка таймаута
        return JsonResponse(
            {'error': 'Сервер не ответил вовремя. Попробуйте обновить страницу или повторите попытку позже.'},
            status=504)

    except Exception as e:
        return JsonResponse({'error': f'Произошла ошибка: {str(e)}'}, status=500)


def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def detail(request, model_name, slug, year, season=None, episode=None):
    models = {
        'movies': Movies,
        'tvshows': TvShows,
        'cartoon': Cartoon,
        'recommendations': Recommendations
    }

    model = models.get(model_name)
    media = get_object_or_404(model, slug=slug)

    # Получение существующего или создание нового цикла
    loop = get_or_create_event_loop()

    season = int(request.GET.get('season', season) or 1)  # Используем сезон 1 по умолчанию
    episode = int(request.GET.get('episode', episode) or 1)  # Используем эпизод 1 по умолчанию

    # Асинхронный вызов функции
    player_data = loop.run_until_complete(get_player_data(slug, model_name, year, season, episode))

    context = {
        'media': media,
        'player_data': player_data,
    }

    return render(request, 'cinema/detail.html', context)


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
