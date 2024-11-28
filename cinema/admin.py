from django.contrib import admin
from .models import Movies, Recommendations, TvShows, Genres


admin.site.register(Movies)
admin.site.register(Recommendations)
admin.site.register(TvShows)
admin.site.register(Genres)
