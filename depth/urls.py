from django.conf.urls.defaults import *
from tdsurface.depth.models import *
from tdsurface.depth.forms import *
from tdsurface.shortcuts import get_object_or_None

def get_active_run() :
    active_run, created = Settings.objects.get_or_create(name='ACTIVE_RUN')
    return active_run.value

urlpatterns = patterns('',
    
    (r'^test/$', 'tdsurface.depth.views.test', {}, 'test'),
    (r'^test/matplotlib/$', 'tdsurface.depth.views.test_matplotlib', {}, 'test_matplotlib'),
    (r'^test/matplotlib/weight_on_bit$', 'tdsurface.depth.views.test_matplotlib_weight_on_bit', {}, 'test_matplotlib_weight_on_bit'),
        
    (r'^well/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'well_create'),
    (r'^well/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'well_update'),    
    (r'^well/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Wells', 'navigation_template': 'well_menu.html'}, 'queryset': Well.objects.all(), 'template_name': 'generic_list.html'}, 'well_list'),
        
    (r'^rig/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Rig', 'navigation_template': 'rig_menu.html'}, 'form_class': RigForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'rig_create'),
    (r'^rig/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Rig', 'navigation_template': 'rig_menu.html'}, 'form_class': RigForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'rig_update'),    
    (r'^rig/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Rigs', 'navigation_template': 'rig_menu.html'}, 'queryset': Rig.objects.all(), 'template_name': 'generic_list.html'}, 'rig_list'),
        
    (r'^wellbore/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Well Bore', 'navigation_template': 'wellbore_menu.html'}, 'model': WellBore, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'wellbore_create'),
    (r'^wellbore/update/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Well Bore', 'navigation_template': 'wellbore_menu.html'}, 'model': WellBore, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'wellbore_update'),    
    (r'^wellbore/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Well Bores', 'navigation_template': 'wellbore_menu.html'}, 'queryset': WellBore.objects.all(), 'template_name': 'generic_list.html'}, 'wellbore_list'),
    
    (r'^tool/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Tool', 'navigation_template': 'tool_list_menu.html'}, 'model': Tool, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'tool_create'),    
    (r'^tool/update/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.depth.views.tool_update', {'extra_context': {'subtitle':'Update Tool', 'navigation_template': 'tool_menu.html'}, }, 'tool_update'),    
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Tool', 'navigation_template': 'tool_menu.html'}, 'model': Tool, 'template_name': 'toolconfig_form.html', 'post_save_redirect': '../../' }, 'tool_config'),
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/pulsepatternprofile/$', 'tdsurface.depth.views.tool_pulse_pattern_profile', {}, 'tool_pulse_pattern_profile'),
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/pullcal/$', 'tdsurface.depth.views.pull_calibration', {}, 'tool_pullcal'),
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/updatecal/$', 'tdsurface.depth.views.tool_calibration_update', {'extra_context': {'subtitle':'Update Calibration Constants', 'navigation_template': 'tool_menu.html'}, 'template_name': 'calibration_form.html', }, 'tool_calibration_update'),
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/settime/$', 'tdsurface.depth.views.set_time', {}, 'tool_set_time'),
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/resettimer/$', 'tdsurface.depth.views.reset_timer', {}, 'tool_reset_timer'),
    (r'^tool/config/(?P<object_id>[\d\-a-f]+)/purgelog/$', 'tdsurface.depth.views.tool_purge_log', {}, 'tool_purge_log'),
    (r'^tool/status/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.depth.views.tool_status', {}, 'tool_status'),
    (r'^tool/sensors/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.depth.views.tool_sensors', {'extra_context': {'subtitle':'Update Calibration Constants', 'navigation_template': 'tool_menu.html'}}, 'tool_sensors'),
    (r'^tool/sensors_json/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.depth.views.tool_sensors_json', {}, 'tool_sensors_json'),
    (r'^tool/detail/(?P<object_id>[\d\-a-f]+)/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'tool_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'tool_detail.html' }, 'tool_detail'),
    (r'^tool/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Tools', 'navigation_template': 'tool_list_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'tool_list.html'}, 'tool_list'),
    
    (r'^run/notes/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Run Note', 'navigation_template': 'run_menu.html'}, 'form_class': RunNotesForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'run_notes_create'),
        
    (r'^run/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Run', 'navigation_template': 'run_menu.html'}, 'form_class': RunForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'run_create'),
    (r'^run/createactive/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Active Run', 'navigation_template': 'run_menu.html'}, 'form_class': RunForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../%(uid)s/activate/' }, 'run_createactive'),        
    (r'^run/(?P<run_id>[\d\-a-f]+)/update/$', 'tdsurface.depth.views.run_update', {'extra_context': {'subtitle':'Update Run', 'navigation_template': 'run_menu.html'}, }, 'run_update'),    
    (r'^run/(?P<object_id>[\d\-a-f]+)/activate/$', 'tdsurface.depth.views.run_activate', {}, 'run_activate'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/detail/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'subtitle':'Run Detail', 'navigation_template': 'run_menu.html', 'active_run': get_active_run },'queryset': Run.objects.all(), 'template_name': 'run_detail.html'}, 'run_detail'),

    (r'^run/(?P<run_id>[\d\-a-f]+)/rolltest/$', 'tdsurface.depth.views.run_roll_test', {'extra_context': {'subtitle':'Update Run', 'navigation_template': 'run_menu.html'}, }, 'run_roll_test'),    

    (r'^run/downloadlog/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.depth.views.run_start_download_log', {}, 'run_download_log'),
    (r'^run/downloadstatus/$', 'tdsurface.depth.views.run_download_status_json', {}, 'run_download_status'),
    (r'^run/downloadcancel/$', 'tdsurface.depth.views.run_download_cancel', {}, 'run_download_cancel'),
    
    (r'^run/(?P<run_id>[\d\-a-f]+)/wits0/log/(?P<num_latest>[\d]+)/(?P<num_skip>[\d]+)/$', 'tdsurface.depth.views.run_wits0_latest', {'extra_context': {'subtitle':'Latest WITS0 Records', 'navigation_template': 'run_menu.html',} }, 'run_wits0_latest'),
    (r'^run/(?P<run_id>[\d\-a-f]+)/wits0/log/(?P<num_latest>[\d]+)/$', 'tdsurface.depth.views.run_wits0_latest', {'extra_context': {'subtitle':'Latest WITS0 Records', 'navigation_template': 'run_menu.html',} }, 'run_wits0_latest'),
    (r'^run/(?P<run_id>[\d\-a-f]+)/wits0/log/$', 'tdsurface.depth.views.run_wits0_latest', {'extra_context': {'subtitle':'Latest WITS0 Records', 'navigation_template': 'run_menu.html',} }, 'run_wits0_latest'),

    (r'^run/(?P<object_id>[\d\-a-f]+)/real_time_json/(?P<num_latest>[\d]+)/$', 'tdsurface.depth.views.run_real_time_json', {}, 'run_real_time_json'),

    (r'^run/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Runs', 'navigation_template': 'run_menu.html', 'active_run': get_active_run }, 'queryset': Run.objects.all(), 'template_name': 'run_list.html'}, 'run_list'),
         
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'mainmenu.html', 'extra_context': { 'active_run': get_active_run }}, 'home'),
    #(r'.*', 'django.views.generic.simple.direct_to_template', {'template': 'mainmenu.html'}),
)
