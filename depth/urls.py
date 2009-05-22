from django.conf.urls.defaults import *
from tdsurface.depth.models import *
from tdsurface.depth.forms import *
from tdsurface.shortcuts import get_object_or_None

def get_active_run() :
    active_run, created = Settings.objects.get_or_create(name='ACTIVE_RUN')
    return active_run.value

def get_active_well() :
    active_well, created = Settings.objects.get_or_create(name='ACTIVE_WELL')
    return active_well.value

def get_active_well_obj() :
    active_well, created = Settings.objects.get_or_create(name='ACTIVE_WELL')
    awo = get_object_or_None(Well, uid = active_well.value)    
    return awo 

urlpatterns = patterns('',
    
    (r'^test/$', 'tdsurface.depth.views.test', {}, 'test'),
    
    (r'^well/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'well_create'),
    (r'^well/createactive/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Active Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../%(uid)s/activate/' }, 'well_createactive'),
    (r'^well/(?P<object_id>[\d\-a-f]+)/activate/$', 'tdsurface.depth.views.well_activate', {}, 'well_activate'),
    (r'^well/(?P<object_id>[\d\-a-f]+)/update/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Well', 'navigation_template': 'well_menu.html'}, 'form_class': WellForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'well_update'),    
    (r'^well/(?P<object_id>[\d\-a-f]+)/real_time_json/(?P<num_latest>[\d]+)/$', 'tdsurface.depth.views.well_real_time_json', {}, 'well_real_time_json'),
    (r'^well/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Wells', 'navigation_template': 'well_menu.html', 'active_well': get_active_well}, 'queryset': Well.objects.all(), 'template_name': 'well_list.html'}, 'well_list'),
        
    (r'^rig/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Rig', 'navigation_template': 'rig_menu.html'}, 'form_class': RigForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'rig_create'),
    (r'^rig/(?P<object_id>[\d\-a-f]+)/update/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Rig', 'navigation_template': 'rig_menu.html'}, 'form_class': RigForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'rig_update'),    
    (r'^rig/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Rigs', 'navigation_template': 'rig_menu.html'}, 'queryset': Rig.objects.all(), 'template_name': 'generic_list.html'}, 'rig_list'),
        
    (r'^wellbore/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Well Bore', 'navigation_template': 'wellbore_menu.html'}, 'model': WellBore, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'wellbore_create'),
    (r'^wellbore/(?P<object_id>[\d\-a-f]+)/update/$', 'django.views.generic.create_update.update_object', {'extra_context': {'subtitle':'Update Well Bore', 'navigation_template': 'wellbore_menu.html'}, 'model': WellBore, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'wellbore_update'),    
    (r'^wellbore/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Well Bores', 'navigation_template': 'wellbore_menu.html'}, 'queryset': WellBore.objects.all(), 'template_name': 'generic_list.html'}, 'wellbore_list'),
    
    (r'^tool/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Tool', 'navigation_template': 'tool_list_menu.html'}, 'model': Tool, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'tool_create'),    
    (r'^tool/(?P<object_id>[\d\-a-f]+)/update/$', 'tdsurface.depth.views.tool_update', {'extra_context': {'subtitle':'Update Tool', 'navigation_template': 'tool_menu.html'}, }, 'tool_update'),        
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'tool_config_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'tool_config_form.html' }, 'tool_config'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/general/$', 'tdsurface.depth.views.tool_general_config', {'extra_context': {'subtitle':'Update Tool', 'navigation_template': 'tool_config_menu.html'}, }, 'tool_general_config'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/motor/$', 'tdsurface.depth.views.tool_motor_config', {'extra_context': {'subtitle':'Tool Motorl Configuration', 'navigation_template': 'tool_config_menu.html'}, }, 'tool_motor_config'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/motor/calibrate/$', 'tdsurface.depth.views.tool_motor_calibrate_json', { }, 'tool_motor_calibrate'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/motor/(?P<command>\w+)/$', 'tdsurface.depth.views.tool_motor_command', { }, 'tool_motor_command'),    
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/pulsepatternprofile/$', 'tdsurface.depth.views.tool_pulse_pattern_profile', {}, 'tool_pulse_pattern_profile'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/pullcal/$', 'tdsurface.depth.views.pull_calibration', {}, 'tool_pullcal'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/updatecal/$', 'tdsurface.depth.views.tool_calibration_update', {'extra_context': {'subtitle':'Update Calibration Constants', 'navigation_template': 'tool_menu.html'}, 'template_name': 'calibration_form.html', }, 'tool_calibration_update'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/settime/$', 'tdsurface.depth.views.set_time', {}, 'tool_set_time'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/resettimer/$', 'tdsurface.depth.views.reset_timer', {}, 'tool_reset_timer'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/config/purgelog/$', 'tdsurface.depth.views.tool_purge_log', {}, 'tool_purge_log'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/status/$', 'tdsurface.depth.views.tool_status', {}, 'tool_status'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/sensors/$', 'tdsurface.depth.views.tool_sensors', {'extra_context': {'subtitle':'Update Calibration Constants', 'navigation_template': 'tool_menu.html'}}, 'tool_sensors'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/sensors_json/$', 'tdsurface.depth.views.tool_sensors_json', {}, 'tool_sensors_json'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/tool_face_zero_json/$', 'tdsurface.depth.views.tool_face_zero_json', {}, 'tool_face_zero_json'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/tool_face_zero_start/$', 'tdsurface.depth.views.tool_face_zero_start', {}, 'tool_face_zero_start'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/frame_mode_buffer/$', 'tdsurface.depth.views.tool_frame_mode_buffer', {}, 'tool_frame_mode_buffer'),    
    (r'^tool/(?P<object_id>[\d\-a-f]+)/tool_face_zero/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'tool_config_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'tool_face_zero.html' }, 'tool_face_zero'),
    (r'^tool/(?P<object_id>[\d\-a-f]+)/detail/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'tool_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'tool_detail.html' }, 'tool_detail'),
    (r'^tool/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Tools', 'navigation_template': 'tool_list_menu.html'}, 'queryset': Tool.objects.all(), 'template_name': 'tool_list.html'}, 'tool_list'),
    
    (r'^run/notes/create/$', 'django.views.generic.create_update.create_object', {'extra_context': {'subtitle':'New Run Note', 'navigation_template': 'run_menu.html'}, 'form_class': RunNotesForm, 'template_name': 'generic_form.html', 'post_save_redirect': '../../' }, 'run_notes_create'),

    (r'^run/create/$', 'tdsurface.depth.views.run_create', {'extra_context': {'subtitle':'New Run', 'navigation_template': 'run_menu.html'}, 'template_name': 'generic_form.html', 'post_save_redirect': '../' }, 'run_create'),
    (r'^run/createactive/$', 'tdsurface.depth.views.run_create', {'extra_context': {'subtitle':'New Active Run', 'navigation_template': 'run_menu.html'}, 'template_name': 'generic_form.html', 'post_save_redirect': '../%(uid)s/activate/' }, 'run_createactive'),            
    (r'^run/(?P<object_id>[\d\-a-f]+)/update/$', 'tdsurface.depth.views.run_update', {'extra_context': {'subtitle':'Update Run', 'navigation_template': 'run_detail_menu.html'}, }, 'run_update'),    
    (r'^run/(?P<object_id>[\d\-a-f]+)/activate/$', 'tdsurface.depth.views.run_activate', {}, 'run_activate'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/detail/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'subtitle':'Run Detail', 'navigation_template': 'run_detail_menu.html', 'active_run': get_active_run },'queryset': Run.objects.all(), 'template_name': 'run_detail.html'}, 'run_detail'),

    (r'^run/(?P<object_id>[\d\-a-f]+)/pipetally/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'run_detail_menu.html', },'queryset': Run.objects.all(), 'template_name': 'run_pipe_tally.html'}, 'run_pipe_tally'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/pipetally/grid/$', 'tdsurface.depth.views.run_pipe_tally_grid', {}, 'run_pipe_tally_grid'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/pipetally/grid/edit/$', 'tdsurface.depth.views.run_pipe_tally_grid_edit', {}, 'run_pipe_tally_grid_edit'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/pipetally/grid/delete/$', 'tdsurface.depth.views.run_pipe_tally_grid_delete', {}, 'run_pipe_tally_grid_delete'),

    (r'^run/(?P<object_id>[\d\-a-f]+)/manualdepth/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'run_detail_menu.html', },'queryset': Run.objects.all(), 'template_name': 'run_manual_depth_grid.html'}, 'run_manual_depth'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/manualdepth/grid/$', 'tdsurface.manual_depth.views.run_manual_depth_grid', {}, 'run_manual_depth_grid'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/manualdepth/grid/edit/$', 'tdsurface.manual_depth.views.run_manual_depth_grid_edit', {}, 'run_manual_depth_grid_edit'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/manualdepth/grid/delete/$', 'tdsurface.manual_depth.views.run_manual_depth_grid_delete', {}, 'run_manual_depth_grid_delete'),

    (r'^run/(?P<object_id>[\d\-a-f]+)/toollog/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'navigation_template': 'run_detail_menu.html', },'queryset': Run.objects.all(), 'template_name': 'run_toollog_grid.html'}, 'run_toollog'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/toollog/grid/$', 'tdsurface.toollog.views.run_toollog_grid', {}, 'run_toollog_grid'),
    
    (r'^run/(?P<object_id>[\d\-a-f]+)/rolltest/$', 'tdsurface.depth.views.run_roll_test', {'extra_context': {'subtitle':'Run Roll Test', 'navigation_template': 'run_detail_menu.html'}, }, 'run_rolltest'),    

    (r'^run/(?P<object_id>[\d\-a-f]+)/download/$', 'django.views.generic.list_detail.object_detail', {'extra_context': {'subtitle':'Run Download Log', 'navigation_template': 'run_detail_menu.html', 'active_run': get_active_run },'queryset': Run.objects.all(), 'template_name': 'run_download.html'}, 'run_download'),
    (r'^run/downloadstart/(?P<object_id>[\d\-a-f]+)/$', 'tdsurface.depth.views.run_start_download_log', {}, 'run_download_start'),
    (r'^run/downloadstatus/$', 'tdsurface.depth.views.run_download_status_json', {}, 'run_download_status'),
    (r'^run/downloadcancel/$', 'tdsurface.depth.views.run_download_cancel', {}, 'run_download_cancel'),

    (r'^run/(?P<object_id>[\d\-a-f]+)/bha/update/$', 'tdsurface.bha.views.bha_update', {'extra_context': {'subtitle':'BHA Update', 'navigation_template': 'run_detail_menu.html',} }, 'bha_update'),    
    (r'^run/(?P<object_id>[\d\-a-f]+)/bha/component/grid/$', 'tdsurface.bha.views.bha_component_grid', {}, 'bha_component_grid'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/bha/component/grid/edit/$', 'tdsurface.bha.views.bha_component_grid_edit', {}, 'bha_component_grid_edit'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/bha/component/grid/delete/$', 'tdsurface.bha.views.bha_component_grid_delete', {}, 'bha_component_grid_delete'),
    
    (r'^run/(?P<object_id>[\d\-a-f]+)/wits0/log/(?P<num_latest>[\d]+)/(?P<num_skip>[\d]+)/$', 'tdsurface.depth.views.run_wits0_latest', {'extra_context': {'subtitle':'Latest WITS0 Records', 'navigation_template': 'run_detail_menu.html',} }, 'run_wits0_latest'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/wits0/log/(?P<num_latest>[\d]+)/$', 'tdsurface.depth.views.run_wits0_latest', {'extra_context': {'subtitle':'Latest WITS0 Records', 'navigation_template': 'run_detail_menu.html',} }, 'run_wits0_latest'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/wits0/log/$', 'tdsurface.depth.views.run_wits0_latest', {'extra_context': {'subtitle':'Latest WITS0 Records', 'navigation_template': 'run_detail_menu.html',} }, 'run_wits0_latest'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/wits0/depth/mwdlog/$', 'tdsurface.depth.views.wits0_depth_to_mwdlog', {}, 'run_wits0_depth_to_mwdlog'),
    (r'^run/(?P<object_id>[\d\-a-f]+)/wits0/depth/rtlog/$', 'tdsurface.depth.views.wits0_depth_to_rtlog', {}, 'run_wits0_depth_to_rtlog'),

    (r'^run/(?P<object_id>[\d\-a-f]+)/manualdepth/mwdlog/$', 'tdsurface.manual_depth.views.manual_depth_to_mwdlog', {}, 'run_manual_depth_to_mwdlog'),    
    (r'^run/(?P<object_id>[\d\-a-f]+)/manualdepth/rtlog/$', 'tdsurface.manual_depth.views.manual_depth_to_rtlog', {}, 'run_manual_depth_to_rtlog'),
    

    (r'^run/$', 'django.views.generic.list_detail.object_list', {'extra_context': {'subtitle':'Runs', 'navigation_template': 'run_menu.html', 'active_run': get_active_run }, 'queryset': Run.objects.all(), 'template_name': 'run_list.html'}, 'run_list'),
         
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'mainmenu.html', 'extra_context': { 'active_well': get_active_well_obj }}, 'home'),
    #(r'.*', 'django.views.generic.simple.direct_to_template', {'template': 'mainmenu.html'}),
)
