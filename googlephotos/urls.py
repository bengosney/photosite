# Django
from django.contrib.auth.decorators import login_required
from django.urls import path

# Locals
from . import views

app_name = "googlephotos"
urlpatterns = [
    path("albums", login_required(views.AlbumListView.as_view()), name="albums"),
    path("albums/<slug:uid>", login_required(views.AlbumView.as_view()), name="album"),
    path("auth/", login_required(views.AuthView.as_view()), name="auth"),
    path("callback/", login_required(views.CallbackView.as_view()), name="callback"),
]
