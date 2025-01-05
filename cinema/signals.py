from math import ceil

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from cinema.models import Movies, TvShows, Cartoon, Genres, Recommendations, Reviews
from django.core.cache import cache


@receiver([post_delete, post_save], sender=Movies)
@receiver([post_delete, post_save], sender=TvShows)
@receiver([post_delete, post_save], sender=Cartoon)
@receiver([post_delete, post_save], sender=Genres)
def delete_media_cache(sender, **kwargs):
    # Очистить кеш всех страниц пагинации для каждого типа медиа
    if sender == Genres:
        cache.delete('genres_data')
        print('Deleted genres cache')
    else:

        # Рассчитываем количество страниц для текущей модели
        total_items = sender.objects.count()  # Общее количество записей
        items_per_page = 25  # Задаем размер страницы, как в пагинаторе
        total_pages = ceil(total_items / items_per_page)  # Рассчитываем количество страниц

        # Удаление кеша для страниц с общим префиксом
        for page_number in range(1, total_pages+1):
            cache_key = f"{sender.__name__}_page_{page_number}"
            cache.delete(cache_key)
        print(f"Deleted cache for {sender.__name__} ({total_pages} pages)")


@receiver([post_save, post_delete], sender=Recommendations)
@receiver([post_save, post_delete], sender=Reviews)
def delete_index_cache(sender, **kwargs):
    if sender == Recommendations:
        cache.delete('rec_movies')
        print('Deleted recommendations cache')
    else:
        cache.delete('reviews')
        print('Deleted reviews cache')

