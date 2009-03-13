from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    (r'^$', 'tdsurface.las.views.las_test', {}, 'las_test'),
    (r'^lasfrommwdlog/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.las.views.las_from_mwdlog', {}, 'las_from_mwdlog'),

)
