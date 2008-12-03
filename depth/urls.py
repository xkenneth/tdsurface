from django.conf.urls.defaults import *

urlpatterns = patterns('',        
    (r'^$', 'tdsurface.depth.views.mainmenu'),
    (r'.*', 'tdsurface.depth.views.mainmenu'),
)