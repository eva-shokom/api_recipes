from django.shortcuts import get_object_or_404, redirect

from .models import Link


def redirection(request, short_url):
    """Перенаправление с короткой ссылки на обычную."""
    full_url = get_object_or_404(Link, short_url=short_url).full_url
    return redirect(full_url)
