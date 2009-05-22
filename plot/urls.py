from django.conf.urls.defaults import *

urlpatterns = patterns('',
        
    (r'^test/matplotlib/$', 'tdsurface.plot.views.test_matplotlib', {}, 'test_matplotlib'),
    (r'^weight_on_bit/$', 'tdsurface.plot.views.test_matplotlib_weight_on_bit', {}, 'test_matplotlib_weight_on_bit'),
    (r'^gammaray/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.plot.views.plot_realtime_gammaray', {}, 'plot_realtime_gammaray'),
    (r'^wellplot/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.plot.views.plot_log_well_path', {}, 'plot_log_well_path'),
            
)
