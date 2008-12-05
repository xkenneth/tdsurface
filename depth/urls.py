from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^wellform.html', 'tdsurface.depth.views.wellform'),                   
    (r'^$', 'tdsurface.depth.views.mainmenu'),
    (r'.*', 'tdsurface.depth.views.mainmenu'),
)