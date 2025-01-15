from django.contrib.auth.models import User
from django.db import models


class Genres(models.Model):
    name = models.CharField(max_length=55, unique=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # Возможность пустого ID, если это необходимо

    def __str__(self):
        return self.name


# Базовая абстрактная модель для фильмов, сериалов и рекомендаций
class BaseMedia(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # Уникальный ID из TMDb
    title = models.CharField(max_length=75, null=True, blank=True)  # Название (общее поле)
    title_en = models.CharField(max_length=75, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)  # Описание
    release_date = models.DateField(null=True, blank=True)  # Дата выхода фильма или шоу
    vote_average = models.FloatField(null=True, blank=True)  # Средний рейтинг
    poster_path = models.URLField(max_length=75, blank=True, null=True)  # Путь к постеру
    slug = models.SlugField(max_length=75, blank=True, null=True, unique=True)
    backdrop_path = models.URLField(max_length=75, blank=True, null=True)
    runtime = models.IntegerField(null=True, blank=True)
    genre = models.ManyToManyField(Genres, blank=True)

    class Meta:
        abstract = True  # Указываем, что модель абстрактная

    def __str__(self):
        return self.title or "Без названия"


# Модель для жанров


# Модель для фильмов
class Movies(BaseMedia):
    pass


# Модель для рекомендаций
class Recommendations(BaseMedia):
    number_of_seasons = models.IntegerField(null=True, blank=True)


# Модель для сериалов
class TvShows(BaseMedia):
    number_of_seasons = models.IntegerField(null=True, blank=True)


class Cartoon(BaseMedia):
    number_of_seasons = models.IntegerField(null=True, blank=True)


class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    date_publish = models.DateField(auto_now_add=True)
    poster = models.URLField()

    def __str__(self):
        return self.user.username

