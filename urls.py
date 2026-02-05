from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/wallet/', include('wallet.urls')),
    path('api/game/', include('game.urls')),
    path('api/admin/', include('admin_panel.urls')),
    path('ws/', include('game.routing')),
    path('swagger/', get_schema_view(
        openapi.Info(title="Prediction API", version="1.0")
    ).with_ui('swagger', cache_timeout=0), name='schema-swagger'),
]
