from django.urls import path

from . import views


app_name = 'link_shortner'

urlpatterns = [
    path('s/<str:short_url>/', views.redirection, name='redirection'),
]
