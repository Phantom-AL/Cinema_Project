from django.contrib import admin

from .models import Movies, Recommendations, TvShows, Genres, Cartoon, Reviews


class BaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average')
    list_filter = ('release_date', 'vote_average')
    prepopulated_fields = {'slug': ("title",)}

    search_fields = ('title', 'title_en')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ("name",)}


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'comment')


admin.site.register(Movies, BaseAdmin)
admin.site.register(Recommendations, BaseAdmin)
admin.site.register(TvShows, BaseAdmin)
admin.site.register(Cartoon, BaseAdmin)
admin.site.register(Genres, GenreAdmin)
admin.site.register(Reviews, ReviewsAdmin)

admin.site.site_header = "Админ панель медиа"
