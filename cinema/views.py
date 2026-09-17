import asyncio

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Prefetch
from django.db.models import Value, CharField
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from cinema.hdrezka import Search

from .forms import RegistrationForm, ReviewForm, CustomLoginForm
from .models import Movies, Recommendations, TvShows, Cartoon, Genres, Reviews


def index(request):
    rec_movies = cache.get('rec_movies')
    model_name = Recommendations.__name__.lower()
    if not rec_movies:
        rec_movies = list(Recommendations.objects.prefetch_related('genre'))
        cache.set('rec_movies', rec_movies, 2592000)

    reviews = cache.get('reviews')
    if not reviews:
        reviews = list(Reviews.objects.select_related('user'))
        cache.set('reviews', reviews, 2592000)

    return render(request, 'cinema/index.html', context={'movies': rec_movies, 'reviews': reviews,
                                                         'model_name': model_name})


def data_paginator(request, model):
    page_number = request.GET.get('page', 1)

    cache_key = f'{model.__name__}_page_{page_number}'
    cache_total_key = f'{model.__name__}_total_results'

    total_result = cache.get(cache_total_key)
    cached_page_data = cache.get(cache_key)

    if not cached_page_data or not total_result:
        data = list(model.objects.prefetch_related('genre'))
        total_result = len(data)

        paginator = Paginator(data, 25)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        cached_page_data = {
            'object_list': list(page_obj.object_list),
            'number': page_obj.number,
            'num_pages': paginator.num_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        }

        cache.set(cache_key, cached_page_data, timeout=2592000)
        cache.set(cache_total_key, total_result, timeout=2592000)

    paginator = Paginator(cached_page_data['object_list'], 25)
    try:
        page_obj = paginator.page(cached_page_data['number'])
    except Exception:
        page_obj = paginator.page(1)

    return page_obj, total_result


def content_list(request, model, model_name):
    page_obj, total_objects = data_paginator(request, model)

    return render(request, 'cinema/movies.html', context={
        'movies': page_obj.object_list,
        'page': page_obj,
        'model_name': model_name,
        'total_objects': total_objects
    })


def movies_by_genre(request, genre_name):
    page_number = request.GET.get('page', 1)

    cache_key = f"movies_by_genre_{genre_name}_page_{page_number}"
    cached_data = cache.get(cache_key)

    if cached_data:
        genre = get_object_or_404(Genres, id=cached_data['genre_id'])
        return render(request, 'cinema/movies.html', {
            'genre': genre,
            'movies': cached_data['object_list'],
            'page': _build_fake_page(cached_data),
            'total_objects': cached_data['total_objects'],
        })

    genre = get_object_or_404(Genres, name=genre_name)

    genre_prefetch = Prefetch('genre', queryset=Genres.objects.filter(id=genre.id))

    movies = Movies.objects.prefetch_related(genre_prefetch).filter(genre=genre).annotate(
        model_name=Value('movies', output_field=CharField())
    )
    tvshows = TvShows.objects.prefetch_related(genre_prefetch).filter(genre=genre).annotate(
        model_name=Value('tvshows', output_field=CharField())
    )
    cartoons = Cartoon.objects.prefetch_related(genre_prefetch).filter(genre=genre).annotate(
        model_name=Value('cartoon', output_field=CharField())
    )

    content = list(movies) + list(tvshows) + list(cartoons)
    paginator = Paginator(content, 25)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    cache_data = {
        'genre_id': genre.id,
        'object_list': list(page_obj.object_list),
        'number': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_objects': paginator.count,
    }
    cache.set(cache_key, cache_data, timeout=2592000)

    return render(request, 'cinema/movies.html', {
        'genre': genre,
        'movies': page_obj.object_list,
        'page': page_obj,
        'total_objects': paginator.count,
    })


def _build_fake_page(cached_data):
    """Відновлює Page-подібний об'єкт з кешованих даних для передачі в шаблон."""
    paginator = Paginator(cached_data['object_list'], 25)
    try:
        return paginator.page(cached_data['number'])
    except Exception:
        return paginator.page(1)


def movies(request):
    return content_list(request, model=Movies, model_name='movies')


def tvshows(request):
    return content_list(request, model=TvShows, model_name='tvshows')


def cartoon(request):
    return content_list(request, model=Cartoon, model_name='cartoon')


def bookmarks(request):
    """Страница закладок"""
    return render(request, 'cinema/bookmarks.html')


class BaseSearchResultView(ListView):
    template_name = 'cinema/search.html'
    model = None

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return self.model.objects.filter(
            Q(title__icontains=query) | Q(title_en__icontains=query)
        ).prefetch_related('genre')

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get('page', 1)
        try:
            return paginator.page(page_number), paginator
        except PageNotAnInteger:
            return paginator.page(1), paginator
        except EmptyPage:
            return paginator.page(paginator.num_pages), paginator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.get_queryset()
        page_obj, paginator = self.paginate_queryset(object_list, 25)

        genre_url = self.request.path_info
        genre_name = genre_url.split('/')[-2]

        if self.model:
            context.update({
                'page': page_obj,
                'object_list': page_obj.object_list,
                'total_objects': paginator.count,
                'model_name': self.model.__name__.lower(),
            })
        else:
            context.update({
                'page': page_obj,
                'object_list': page_obj.object_list,
                'total_objects': paginator.count,
                'genre_name': genre_name
            })

        return context


class SearchResultsMovieView(BaseSearchResultView):
    model = Movies


class SearchResultsTvShowsView(BaseSearchResultView):
    model = TvShows


class SearchResultsCartoonView(BaseSearchResultView):
    model = Cartoon


class SearchResultsAllView(BaseSearchResultView):
    def get_all_media(self, query, genre_out_url):
        movies_queryset = Movies.objects.prefetch_related('genre').filter(
            (Q(title__icontains=query) | Q(title_en__icontains=query)) & Q(genre=genre_out_url)
        ).annotate(model_name=Value('movies', output_field=CharField()))
        tvshows_queryset = TvShows.objects.prefetch_related('genre').filter(
            (Q(title__icontains=query) | Q(title_en__icontains=query)) & Q(genre=genre_out_url)
        ).annotate(model_name=Value('tvshows', output_field=CharField()))
        cartoon_queryset = Cartoon.objects.prefetch_related('genre').filter(
            (Q(title__icontains=query) | Q(title_en__icontains=query)) & Q(genre=genre_out_url)
        ).annotate(model_name=Value('cartoon', output_field=CharField()))

        content_lst = list(movies_queryset) + list(tvshows_queryset) + list(cartoon_queryset)

        return content_lst

    def get_queryset(self):
        query = self.request.GET.get('q', '')

        genre_url = self.request.path_info
        print(genre_url)

        genre_name = genre_url.split('/')[-2]
        genre_out_url = get_object_or_404(Genres, name=genre_name)

        return self.get_all_media(query, genre_out_url)


# Асинхронная функция для загрузки данных о плеере
async def get_player_data(slug, model_name, year, season, episode, translator_id=None):
    try:
        search_results = await Search(slug).get_page(1)

        first_result = None
        for result in search_results:
            start_year = result.info.year

            if str(start_year) == str(year):
                first_result = result
                break

        if first_result is None:
            return 'Год не найден !!!'


        player = await first_result.player

        if not translator_id:
            translator_id = 238

        try:
            available_seasons = await player.get_episodes(translator_id)
            stream = await player.get_stream(int(season), int(episode), translator_id)
            available_seasons_list = list(available_seasons.items())

        except:
            stream = await player.get_stream(translator_id)
            available_seasons_list = None

        subtitles_urls = {
            'english_sub': stream.subtitles.subtitle_names.get('English').url if stream.subtitles.subtitle_names.get(
                'English') else None,
            'russian_sub': stream.subtitles.subtitle_names.get('Русский').url if stream.subtitles.subtitle_names.get(
                'Русский') else None
        }

        video_urls = {
            'url_360p': stream.video[360].raw_data.get('360p'),
            'url_720p': stream.video[720].raw_data.get('720p'),
            'url_1080p': stream.video[1080].raw_data.get('1080p'),
        }
        print('LOCKal ', video_urls)
        return {
            'video_urls': video_urls,
            'subtitles_url': subtitles_urls,
            'available_seasons_list': available_seasons_list,
            'translators': list(player.post.translators.name_id.items())
        }

    except TimeoutError:
        return JsonResponse(
            {'error': 'Сервер не ответил вовремя. Попробуйте обновить страницу или повторите попытку позже.'},
            status=504)

    except Exception as e:
        return JsonResponse({'error': f'Произошла ошибка: {str(e)}'}, status=500)

    except:
        print('Ошибка поиска по слагу ')


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

    loop = get_or_create_event_loop()

    translator_id = request.GET.get('translator_id', '238')
    season = int(request.GET.get('season', season) or 1)
    episode = int(request.GET.get('episode', episode) or 1)

    player_data = loop.run_until_complete(get_player_data(slug, model_name, year, season, episode, translator_id))

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.poster = media.poster_path

                content_type = ContentType.objects.get_for_model(media)
                review.content_type = content_type
                review.object_id = media.id
                review.model_name = model_name
                review.save()
                return redirect(request.path)
        else:
            return redirect('login')

    context = {
        'media': media,
        'player_data': player_data,
        'current_translator_id': translator_id,
    }

    return render(request, 'cinema/detail.html', context)


def genre(request):
    genres_data = cache.get('genres_data')

    if not genres_data:
        genres = list(Genres.objects.all())

        movies = Movies.objects.prefetch_related('genre')
        tv_shows = TvShows.objects.prefetch_related('genre')
        cartoons = Cartoon.objects.prefetch_related('genre')

        genre_media_map = {g: [] for g in genres}
        used_posters = set()

        for media_set in [movies, tv_shows, cartoons]:
            for item in media_set:
                for g in item.genre.all():
                    if g in genre_media_map and item.poster_path not in used_posters:
                        if len(genre_media_map[g]) < 3:
                            genre_media_map[g].append(item)
                            used_posters.add(item.poster_path)

        genres_data = [
            {
                'genre': {'id': g.id, 'name': g.name},
                'media': media_list
            }
            for g, media_list in genre_media_map.items()
        ]

        cache.set('genres_data', genres_data, timeout=2592000)

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