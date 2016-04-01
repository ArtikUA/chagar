from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^chat/', TemplateView.as_view(template_name='chat.html')),
    url(r'^$', TemplateView.as_view(template_name='canvas.html')),
    url(r'^background/', TemplateView.as_view(template_name='background.html')),
]
urlpatterns += staticfiles_urlpatterns()
