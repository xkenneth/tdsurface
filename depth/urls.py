from django.conf.urls.defaults import *
from tdsurface.depth.models import *
from tdsurface.depth.forms import *


urlpatterns = patterns('',
    
    (r'^well/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }),
    (r'^well/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }),
    (r'^well/list/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Wells', 'navigation_template': 'well_menu.html'}, 'queryset': Well.objects.all(), 'template_name': 'generic_list.html'}),
    (r'^well/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Wells', 'navigation_template': 'well_menu.html'}, 'queryset': Well.objects.all(), 'template_name': 'generic_list.html'}),
        
    (r'^rig/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Rig', 'navigation_template': 'rig_menu.html'}, 'model': Rig, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }),
    (r'^rig/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Rig', 'navigation_template': 'rig_menu.html'}, 'model': Rig, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }),
    (r'^rig/list/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Rigs', 'navigation_template': 'rig_menu.html'}, 'queryset': Rig.objects.all(), 'template_name': 'generic_list.html'}),
    (r'^rig/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Rigs', 'navigation_template': 'rig_menu.html'}, 'queryset': Rig.objects.all(), 'template_name': 'generic_list.html'}),
        
    (r'^wellbore/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'Update Well Bore', 'navigation_template': 'wellbore_menu.html'}, 'model': WellBore, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }),
    (r'^wellbore/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'New Well Bore', 'navigation_template': 'wellbore_menu.html'}, 'model': WellBore, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }),
    (r'^wellbore/list/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Well Bores', 'navigation_template': 'wellbore_menu.html'}, 'queryset': WellBore.objects.all(), 'template_name': 'generic_list.html'}),
    (r'^wellbore/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Well Bores', 'navigation_template': 'wellbore_menu.html'}, 'queryset': WellBore.objects.all(), 'template_name': 'generic_list.html'}),
    
    (r'^tool/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Tool', 'navigation_template': 'tool_menu.html'}, 'model': Tool, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }),
    (r'^tool/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Tool', 'navigation_template': 'tool_menu.html'}, 'model': Tool, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }),
    (r'^tool/list/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Tools', 'navigation_template': 'tool_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'generic_list.html'}),
    (r'^tool/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Tools', 'navigation_template': 'tool_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'generic_list.html'}),
        
    (r'^run/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Run', 'navigation_template': 'run_menu.html'}, 'model': Run, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }),
    (r'^run/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Run', 'navigation_template': 'run_menu.html'}, 'model': Run, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }),
    (r'^run/list/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Runs', 'navigation_template': 'run_menu.html'}, 'queryset': Run.objects.all(), 'template_name': 'generic_list.html'}),
    (r'^run/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Runs', 'navigation_template': 'run_menu.html'}, 'queryset': Run.objects.all(), 'template_name': 'generic_list.html'}),
     
    
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'mainmenu.html'}),
    #(r'.*', 'django.views.generic.simple.direct_to_template', {'template': 'mainmenu.html'}),
)