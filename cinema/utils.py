import requests
from django.utils.text import slugify
from film_base import settings
from .models import Genres, Recommendations

API_KEY = settings.API_KEY
API_KEY_OMDB = settings.API_KEY_OMDB
BASE_URL = 'https://api.themoviedb.org/3'
BASE_URL_OMDB = 'https://www.omdbapi.com/'


def fetch_and_save_genres():
    genres_url = f'{BASE_URL}/genre/movie/list'
    genres_tv_url = f'{BASE_URL}/genre/tv/list'
    params_genres = {'api_key': API_KEY, 'language': 'ru-RU'}

    response_movie_genres = requests.get(genres_url, params=params_genres)
    response_tv_genres = requests.get(genres_tv_url, params=params_genres)

    if response_movie_genres.status_code == 200 and response_tv_genres.status_code == 200:
        genres_movie_data = response_movie_genres.json().get('genres', [])
        genres_tv_data = response_tv_genres.json().get('genres', [])

        for genre_movie in genres_movie_data:
            Genres.objects.get_or_create(
                name=genre_movie['name'],
                defaults={'tmdb_id': genre_movie['id']}
            )

        for genre_tv in genres_tv_data:
            Genres.objects.get_or_create(
                name=genre_tv['name'],
                defaults={'tmdb_id': genre_tv['id']}
            )
        print("Жанры успешно обновлены.")
    else:
        print(f"Ошибка при получении жанров: {response_movie_genres.status_code}, {response_tv_genres.status_code}")


def get_imdb_rating(title, year):
    params = {'apikey': API_KEY_OMDB,
              's': title,
              'y': year
              }

    response = requests.get(BASE_URL_OMDB, params=params)

    if response.status_code == 200:
        response_data = response.json()
        search_results = response_data.get('Search', [])

        if search_results:
            imdb_id = search_results[0].get('imdbID', None)
        else:
            print('No results found')
            return None
        print(f'imdb_id - {imdb_id}')

        response_rating = requests.get(BASE_URL_OMDB, params={'apikey': API_KEY_OMDB, 'i': imdb_id})

        if response_rating.status_code == 200:
            rating = response_rating.json().get('imdbRating', '')
            if rating == "N/A" or rating == '':
                print(f'rating {rating} is not a valid number')
                return None
            try:
                return float(rating)
            except ValueError:
                print(f'Error converting to float: {rating}')
                return None
        else:
            print(f"Error fetching rating: {response_rating.status_code}")
    else:
        print(f"Error fetching movie data: {response.status_code}")

    return None


def fetch_and_save_media(media_model, page_start=1, page_end=3, with_genres=False, is_tv_show=False):
    count = 0

    # Загрузка жанров из базы данных
    genres_dict = {genre.tmdb_id: genre for genre in Genres.objects.all()}

    for i in range(page_start, page_end):
        # URL для фильмов или сериалов
        url_movie = f'{BASE_URL}/discover/movie'
        url_tv = f'{BASE_URL}/discover/tv'

        # Параметры запроса по умолчанию
        params_ru = {
            'api_key': API_KEY,
            'language': 'ru-RU',
            'page': i,
            'vote_count.gte': 1500,
            'without_genres': '16'  # Исключаем мультфильмы
        }
        params_en = {
            'api_key': API_KEY,
            'page': i,
            'vote_count.gte': 1500,
            'without_genres': '16'  # Исключаем мультфильмы
        }

        # Если указан параметр with_genres, заменяем without_genres на with_genres
        if with_genres:
            params_ru["with_genres"] = params_ru.pop("without_genres")  # Удаляем параметр without_genres
            params_en["with_genres"] = params_en.pop("without_genres")

        # Выбор URL в зависимости от типа медиа
        if is_tv_show:
            response_ru = requests.get(url_tv, params=params_ru)
            response_en = requests.get(url_tv, params=params_en)
        else:
            response_ru = requests.get(url_movie, params=params_ru)
            response_en = requests.get(url_movie, params=params_en)

        if response_ru.status_code == 200 and response_en.status_code == 200:
            data_ru = response_ru.json().get('results', [])
            data_en = response_en.json().get('results', [])

            for media_ru, media_en in zip(data_ru, data_en):

                detail_url = f'{BASE_URL}/{'tv' if is_tv_show else 'movie'}/{media_ru.get('id')}'

                detail_response = requests.get(detail_url, params={'api_key': API_KEY, 'language': 'ru'})

                runtime = None
                number_of_seasons = None

                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    if is_tv_show:
                        number_of_seasons = detail_data.get('number_of_seasons', None)
                        runtime = detail_data.get('last_episode_to_air').get('runtime', None)
                    else:
                        runtime = detail_data.get('runtime', None)
                else:
                    print(f'Something went wrong {detail_response.status_code}')

                # Сопоставление жанров
                genre_ids = media_ru.get('genre_ids', [])

                # Список объектов жанров (x:000adr, x:012adr)
                genre_instances = [genres_dict.get(genre_id) for genre_id in genre_ids if genre_id in genres_dict]

                # Название и дата выпуска зависят от типа медиа
                if is_tv_show:
                    title = media_ru.get('name', 'Без названия')
                    title_en = media_en.get('name', 'Без названия')
                    release_date = media_ru.get('first_air_date', None)
                else:
                    title = media_ru.get('title', 'Без названия')
                    title_en = media_en.get('title', 'Без названия')
                    release_date = media_ru.get('release_date', None)

                # Получаем рейтинг IMDb
                rating_imdb = get_imdb_rating(title=title_en, year=release_date[-4:] if release_date else None)

                # преобразуем строку title в slug
                generated_slug = slugify(title_en)

                # Создаём словарь defaults с общими полями
                defaults = {
                    'title': title,
                    'slug': generated_slug,
                    'overview': media_ru.get('overview', ''),
                    'release_date': release_date,
                    'vote_average': rating_imdb if rating_imdb else round(media_ru.get('vote_average', 1)),
                    'poster_path': f"https://image.tmdb.org/t/p/original{media_en.get('poster_path')}" if media_en.get(
                        'poster_path') else None,
                    'backdrop_path': f"https://image.tmdb.org/t/p/original{media_en.get('backdrop_path')}" if media_en.get(
                        'backdrop_path') else None,
                    'runtime': runtime,
                }

                # Условно добавляем number_of_seasons для сериалов
                if is_tv_show:
                    defaults['number_of_seasons'] = number_of_seasons

                # Создаём или обновляем запись
                media, created = media_model.objects.update_or_create(
                    tmdb_id=media_ru.get('id'),
                    defaults=defaults
                )

                # Привязка жанров
                media.genre.set(genre_instances)
                media.save()

                count += 1

    return f'total_results: {count}'


def fetch_and_save_recommendations(title_search, media):
    count = 0
    if media in ('movie', 'tv',):
        url_title = f'{BASE_URL}/search/{media}?query={title_search}'
    else:
        return f'{media} должно быть movie или tv'
    genres_dict = {genre.tmdb_id: genre for genre in Genres.objects.all()}

    params_ru = {
        'api_key': API_KEY,
        'language': 'ru-RU',
    }

    params_en = {
        'api_key': API_KEY
    }

    response_ru = requests.get(url_title, params=params_ru)
    response_en = requests.get(url_title, params=params_en)

    if response_ru.status_code == 200 and response_en.status_code == 200:
        try:
            data_ru = response_ru.json().get('results', [])[0]
            data_en = response_en.json().get('results', [])[0]

            detail_url = f'{BASE_URL}/{'tv' if media == 'tv' else 'movie'}/{data_ru.get('id')}'

            detail_response = requests.get(detail_url, params={'api_key': API_KEY, 'language': 'ru'})

            runtime = None
            number_of_seasons = None

            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if media == 'tv':
                    number_of_seasons = detail_data.get('number_of_seasons', None)
                    runtime = detail_data.get('last_episode_to_air').get('runtime', None)
                else:
                    runtime = detail_data.get('runtime', None)
            else:
                print(f'Something went wrong {detail_response.status_code}')

            genre_ids = data_ru.get("genre_ids", [])
            instance_genre = [genres_dict.get(genre_id) for genre_id in genre_ids if genre_id in genres_dict]

            if media == 'movie':
                title = data_ru.get('title', 'Без названия')
                title_en = data_en.get('title', 'Without name')
                release_date = data_ru.get('release_date', '')
            else:
                title = data_ru.get('name', 'Без названия')
                title_en = data_en.get('name', 'Without name')
                release_date = data_ru.get('first_air_date', '')

            rating_imdb = get_imdb_rating(title_search, year=release_date[-4:] if release_date else None)
            generated_slug = slugify(title_en)

            defaults = {
                'title': title,
                'release_date': release_date,
                'slug': generated_slug,
                'overview': data_ru.get('overview', ''),
                'vote_average': rating_imdb if rating_imdb else round(data_ru.get('vote_average'), 1),
                'poster_path': f"https://image.tmdb.org/t/p/w500{data_en.get('poster_path')}" if data_en.get(
                    'poster_path') else None,
                'backdrop_path': f"https://image.tmdb.org/t/p/original{data_en.get('backdrop_path')}" if data_en.get(
                    'backdrop_path') else None,
                'runtime': runtime
            }

            if media == 'tv':
                defaults['number_of_seasons'] = number_of_seasons

            recommendation, created = Recommendations.objects.update_or_create(
                tmdb_id=data_ru.get('id'),
                defaults=defaults
            )

            recommendation.genre.set(instance_genre)
            recommendation.save()

            count += 1

        except IndexError:
            print(f'Неверное title_search или media: {title_search} - {media}')

    return f'total_results: {count}'
