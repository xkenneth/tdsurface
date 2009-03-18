from django.conf.urls.defaults import *

urlpatterns = patterns('',
        
    (r'^test/matplotlib/$', 'tdsurface.plot.views.test_matplotlib', {}, 'test_matplotlib'),
    (r'^test/matplotlib/weight_on_bit$', 'tdsurface.plot.views.test_matplotlib_weight_on_bit', {}, 'test_matplotlib_weight_on_bit'),
            
)
