from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Genres(models.Model):
    name = models.CharField(max_length=55, unique=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # Возможность пустого ID, если это необходимо
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def __str__(self):
        return self.name


# Базовая абстрактная модель для фильмов, сериалов и рекомендаций
class BaseMedia(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # Уникальный ID из TMDb
    title = models.CharField(max_length=75, null=True, blank=True, db_index=True)  # Название (общее поле)
    title_en = models.CharField(max_length=75, null=True, blank=True, db_index=True)
    overview = models.TextField(null=True, blank=True)  # Описание
    release_date = models.DateField(null=True, blank=True)  # Дата выхода фильма или шоу
    vote_average = models.FloatField(null=True, blank=True)  # Средний рейтинг
    poster_path = models.URLField(max_length=75, blank=True, null=True)  # Путь к постеру
    slug = models.SlugField(max_length=75, blank=True, null=True, unique=True)
    backdrop_path = models.URLField(max_length=75, blank=True, null=True)
    runtime = models.IntegerField(null=True, blank=True)
    genre = models.ManyToManyField(Genres, blank=True, db_index=True)

    class Meta:
        abstract = True  # Указываем, что модель абстрактная

    def __str__(self):
        return self.title or "Без названия"


# Модель для жанров


# Модель для фильмов
class Movies(BaseMedia):
    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "movies"


# Модель для рекомендаций
class Recommendations(BaseMedia):
    number_of_seasons = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "recommendation"
        verbose_name_plural = "recommendations"


# Модель для сериалов
class TvShows(BaseMedia):
    number_of_seasons = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Tvshow"
        verbose_name_plural = "Tvshows"


class Cartoon(BaseMedia):
    number_of_seasons = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Cartoon"
        verbose_name_plural = "Cartoons"


class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    date_publish = models.DateField(auto_now_add=True)
    poster = models.URLField(null=True, blank=True)
    model_name = models.CharField(max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_model = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return self.user.username
