from django import forms

form_css = '/tdsurface/media/css/forms.css'


class LasFromMWDLogForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }

    # depth_source = forms.ChoiceField(required=True, choices=[('wits0','WITS0'), ('manualdepth','Manual Depth')])
    elapsed_time = forms.BooleanField(required=False)
    status = forms.BooleanField(required=False)
    temperature_f = forms.BooleanField(required=False)
    temperature_c = forms.BooleanField(required=False)    
    azimuth = forms.BooleanField(required=False)
    inclination = forms.BooleanField(required=False)
    tool_face_gravity = forms.BooleanField(required=False)
    tool_face_magnetic = forms.BooleanField(required=False)
    gravity_x = forms.BooleanField(required=False)
    gravity_y = forms.BooleanField(required=False)
    gravity_z = forms.BooleanField(required=False)
    total_gravity = forms.BooleanField(required=False)
    magnetic_x = forms.BooleanField(required=False)
    magnetic_y = forms.BooleanField(required=False)
    magnetic_z = forms.BooleanField(required=False)
    total_magnetic = forms.BooleanField(required=False)

class LasFromMWDGammaLogForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }
    
    elapsed_time = forms.BooleanField(required=False)
    status = forms.BooleanField(required=False)    
    gamma_ray = forms.BooleanField(required=False)        

class LasFromRTLogForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }
    
    status = forms.BooleanField(required=False)
    temperature_f = forms.BooleanField(required=False)    
    gamma_ray = forms.BooleanField(required=False)
    azimuth = forms.BooleanField(required=False)
    inclination = forms.BooleanField(required=False)
    tool_face = forms.BooleanField(required=False)
    gravity = forms.BooleanField(required=False)    
    magnetic = forms.BooleanField(required=False)
