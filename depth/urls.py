from django.conf.urls.defaults import *
from tdsurface.depth.models import *
from tdsurface.depth.forms import *

urlpatterns = patterns('',
    #(r'^wellform.html', 'tdsurface.depth.views.wellform'),
    (r'^wellcreate', 'django.views.generic.create_update.create_object', {'form_class': WellForm, 'template_name': 'wellform.html' }),
    (r'^wellupdate', 'django.views.generic.create_update.update_object', {'form_class': WellForm, 'template_name': 'wellform.html' }),
    (r'^$', 'tdsurface.depth.views.mainmenu'),
    (r'.*', 'tdsurface.depth.views.mainmenu'),
)