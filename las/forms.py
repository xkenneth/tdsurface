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
    temperature = forms.BooleanField(required=False)    
    gamma_ray_0 = forms.BooleanField(required=False)
    gamma_ray_1 = forms.BooleanField(required=False)
    gamma_ray_2 = forms.BooleanField(required=False)
    gamma_ray_3 = forms.BooleanField(required=False)    
    gravity_x = forms.BooleanField(required=False)
    gravity_y = forms.BooleanField(required=False)
    gravity_z = forms.BooleanField(required=False)
    total_gravity = forms.BooleanField(required=False)
    magnetic_x = forms.BooleanField(required=False)
    magnetic_y = forms.BooleanField(required=False)
    magnetic_z = forms.BooleanField(required=False)
    total_magnetic = forms.BooleanField(required=False)
