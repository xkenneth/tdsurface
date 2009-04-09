from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    (r'^$', 'tdsurface.las.views.las_test', {}, 'las_test'),
    (r'^lasfrommwdlog/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.las.views.las_from_mwdlog', {}, 'las_from_mwdlog'),
    (r'^lasfrommwdgammalog/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.las.views.las_from_mwdgammalog', {}, 'las_from_mwdgammalog'),
    (r'^lasfromrtlog/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.las.views.las_from_rtlog', {}, 'las_from_rtlog'),
)
