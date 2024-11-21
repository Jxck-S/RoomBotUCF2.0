from django.contrib import admin
from django.urls import path
from room_bot_app import views  # Import the view from the app
from django.urls import path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_reservations, name='get_reservations'),  # Root URL points to the view
    path("update-credentials/", views.update_credentials, name="update_credentials"),
    path("add-user/", views.add_user, name="add_user"),
    path('stats/', views.stats, name='stats'),
    re_path(r'^(?P<date>\d{4}-\d{2}-\d{2})?/?$', views.get_reservations, name='get_reservations')
]
