from django import template

register = template.Library()


def get_hour_word(hours):
    if hours % 10 == 1 and hours % 100 != 11:
        return "час"
    elif 2 <= hours % 10 <= 4 and not (12 <= hours % 100 <= 14):
        return "часа"
    else:
        return "часов"


@register.filter
def format_runtime(value):
    try:
        value = int(value)
        if value >= 60:
            hours = value // 60
            minutes = value % 60
            hour_word = get_hour_word(hours)
            if minutes == 0:
                return f"{hours} {hour_word}"
            return f"{hours} {hour_word} {minutes} мин"
        return f"{value} мин"
    except (ValueError, TypeError):
        return None
