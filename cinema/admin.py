from django.contrib import admin

from .models import Movies, Recommendations, TvShows, Genres, Cartoon, Reviews


class BaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average')
    prepopulated_fields = {'slug': ("title",)}

    search_fields = ('title', 'release_date')
    filter = ['release_date', 'vote_average']


admin.site.register(Movies, BaseAdmin)
admin.site.register(Recommendations, BaseAdmin)
admin.site.register(TvShows, BaseAdmin)
admin.site.register(Cartoon, BaseAdmin)
admin.site.register(Genres)
admin.site.register(Reviews)
