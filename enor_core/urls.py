"""
URL configuration for enor_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views as home_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("",home_views.home,name='home'),
    path("search/",home_views.search_view,name="search"),
    path("about/",home_views.about_view,name="about"),
    path("privacy/",home_views.privacy_view,name="privacy"),
    path("terms/",home_views.terms_service,name="terms"),
    path("hotdeals/",home_views.hot_deals,name="hotdeals"),
    path("users/",include('enor_profile.urls')),
    path("store/",include('enor_store.urls')),
    path('cart/', include('enor_cart.urls')),
    path('orders/', include('enor_order.urls')),
    path('content/',include('enor_content.urls')),
    path('enor_admin/',include('enor_admin.urls'))

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)