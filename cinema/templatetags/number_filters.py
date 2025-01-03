from django import template

register = template.Library()


@register.filter
def pluralize_season(number):
    if 11 <= number % 100 <= 19:
        return f"{number} сезонов"
    elif number % 10 == 1:
        return f"{number} сезон"
    elif 2 <= number % 10 <= 4:
        return f"{number} сезона"
    else:
        return f"{number} сезонов"
