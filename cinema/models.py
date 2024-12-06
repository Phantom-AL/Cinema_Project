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
    overview = models.TextField(null=True, blank=True)  # Описание
    release_date = models.DateField(null=True, blank=True)  # Дата выхода фильма или шоу
    vote_average = models.FloatField(null=True, blank=True)  # Средний рейтинг
    poster_path = models.URLField(max_length=500, blank=True, null=True)  # Путь к постеру
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
    pass


# Модель для сериалов
class TvShows(BaseMedia):
    pass


class Cartoon(BaseMedia):
    pass


class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    date_publish = models.DateField(auto_now_add=True)
    poster = models.URLField()

    def __str__(self):
        return self.user.username

