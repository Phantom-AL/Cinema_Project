import requests

from film_base import settings
from .models import Genres, Cartoon

API_KEY = settings.API_KEY
BASE_URL = 'https://api.themoviedb.org/3'


def fetch_and_save_media(media_model, page_start=1, page_end=3, is_tv_show=False):
    count = 0

    genres_url = f'{BASE_URL}/genre/movie/list'
    genres_tv_url = f'{BASE_URL}/genre/tv/list'
    params_genres = {'api_key': API_KEY, 'language': 'ru-RU'}
    response_movie_genres = requests.get(genres_url, params=params_genres)
    response_tv_genres = requests.get(genres_tv_url, params=params_genres)

    genres_dict = {}

    if response_movie_genres.status_code == 200 and response_tv_genres.status_code == 200:
        genres_movie_data = response_movie_genres.json().get('genres', [])
        genres_tv_data = response_tv_genres.json().get('genres', [])

        for genre_movie in genres_movie_data:
            genre_instance_movie = Genres.objects.get_or_create(
                name=genre_movie['name'],
                defaults={'tmdb_id': genre_movie['id']}
            )[0]
            genres_dict[genre_movie['id']] = genre_instance_movie

        for genre_tv in genres_tv_data:
            genre_instance_tv = Genres.objects.get_or_create(
                name=genre_tv['name'],
                defaults={'tmdb_id': genre_tv['id']}
            )[0]
            genres_dict[genre_tv['id']] = genre_instance_tv
    else:
        print(f"Ошибка при получении жанров: {response_movie_genres.status_code}")
        return count

    for i in range(page_start, page_end):
        url_movie = f'{BASE_URL}/discover/movie'
        url_tv = f'{BASE_URL}/discover/tv'

        # Параметры для запросов
        params_ru = {'api_key': API_KEY,
                     "language": "ru-RU",
                     "page": i,
                     "vote_count.gte": 1500,
                     "without_genres": "16"
                     }

        params_en = {'api_key': API_KEY,
                     "language": "en-US",
                     "page": i,
                     "vote_count.gte": 1500,
                     "without_genres": "16"
                     }

        # Запросы
        if is_tv_show:
            response_ru = requests.get(url_tv, params=params_ru)
            response_en = requests.get(url_tv, params=params_en)
        else:
            response_ru = requests.get(url_movie, params=params_ru)
            response_en = requests.get(url_movie, params=params_en)

        if response_ru.status_code == 200 and response_en.status_code == 200:
            data_ru = response_ru.json().get('results', [])
            data_en = response_en.json().get('results', [])

            print(data_ru)
            print(data_en)

            # Сопоставляем фильмы или рекомендации
            for media_ru, media_en in zip(data_ru, data_en):
                if media_ru.get('id') == media_en.get('id'):
                    # Преобразуем ID жанров в объекты Genre
                    genre_ids = media_ru.get('genre_ids', [])
                    genre_instances = [genres_dict.get(genre_id) for genre_id in genre_ids if genre_id in genres_dict]

                    # Если это ТВ-шоу, используем title и release_date
                    if is_tv_show:
                        title = media_ru.get('name', 'Без названия')
                        release_date = media_ru.get('first_air_date', None)
                    else:
                        title = media_ru.get('title', 'Без названия')
                        release_date = media_ru.get('release_date', None)

                    # Создаем или обновляем запись в базе данных
                    media = media_model.objects.update_or_create(
                        tmdb_id=media_ru.get('id'),
                        defaults={
                            "title": title,
                            "overview": media_ru.get('overview', ''),
                            "vote_average": round(media_ru.get('vote_average', 0.0), 1),
                            "poster_path": f"https://image.tmdb.org/t/p/w500{media_en.get('poster_path')}" if media_en.get(
                                'poster_path') else None,
                            "release_date": release_date,  # Используем release_date
                        }
                    )[0]

                    # Связываем жанры с объектом
                    media.genre.set(genre_instances)
                    media.save()

                    count += 1
        else:
            print(f"Ошибка API: RU-{response_ru.status_code}, EN-{response_en.status_code}")
    return count


def fetch_and_save_cartoon(page_start=1, page_end=3, is_tv_show=False):
    count = 0
    for i in range(page_start, page_end):

        url_cartoon_movie = f'{BASE_URL}/discover/movie'
        url_cartoon_tv = f'{BASE_URL}/discover/tv'

        cartoon_params_ru = {
            'api_key': API_KEY,
            'language': 'ru-Ru',
            'page': i,
            'with_genres': 16,
            'vote_count.gte': 1500

        }

        cartoon_params_en = {
            'api_key': API_KEY,
            'page': i,
            'with_genres': 16,
            'vote_count.gte': 1500

        }

        if is_tv_show:
            response_ru = requests.get(url_cartoon_tv, params=cartoon_params_ru)
            response_en = requests.get(url_cartoon_tv, params=cartoon_params_en)
        else:
            response_ru = requests.get(url_cartoon_movie, params=cartoon_params_ru)
            response_en = requests.get(url_cartoon_movie, params=cartoon_params_en)

        if response_ru.status_code == 200 and response_en.status_code == 200:

            data_ru = response_ru.json().get('results', [])
            data_en = response_en.json().get('results', [])

            print(data_ru)
            print(data_en)

            for media_ru, media_en in zip(data_ru, data_en):

                if is_tv_show:
                    title = media_ru.get('name', 'Без названия')
                    release_date = media_ru.get('first_air_date', None)
                else:
                    title = media_ru.get('title', 'Без названия')
                    release_date = media_ru.get('release_date', None)

                Cartoon.objects.update_or_create(
                    tmdb_id=media_ru.get('id'),
                    defaults={
                        'title': title,
                        'overview': media_ru.get('overview', ''),
                        'release_date': release_date,
                        'vote_average': round(media_ru.get('vote_average', 0.0), 1),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{media_en.get('poster_path')}" if media_en.get(
                            'poster_path') else None,

                    }
                )
                count += 1

    return count
