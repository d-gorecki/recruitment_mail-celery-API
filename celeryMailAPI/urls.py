"""celeryMailAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from API.views.email import EmailViewSet
from API.views.mailbox import MailboxViewSet
from API.views.template import TemplateViewSet
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"mailbox", MailboxViewSet, basename="mailbox")
router.register(r"template", TemplateViewSet, basename="template")
router.register(r"email", EmailViewSet, basename="email")

urlpatterns = [path("admin/", admin.site.urls), path("", include(router.urls))]
