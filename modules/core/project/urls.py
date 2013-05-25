from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
#!chuck_renders URL_MODULES #!end

admin.autodiscover()

#!chuck_renders URLS
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    #url(r'^pagina1$', TemplateView.as_view(template_name="pagina1.html", get_context_data=lambda: {'pagina': 'pagina1'})),
)

# static media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
#!end

# handler500 = 'main.views.nondefault_500_error'
