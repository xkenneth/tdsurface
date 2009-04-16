from django.http import HttpResponse
from django.template import loader, Context
from django.template import RequestContext 
from django.shortcuts import render_to_response
from django.db.models import Avg, Max, Min, Count

from las.file import *
from las.headers import *
from datetime import date, datetime

from tdsurface.depth.models import ToolMWDLog
from tdsurface.depth.models import ToolMWDLogGamma
from tdsurface.depth.models import ToolMWDRealTime
from tdsurface.depth.models import Run
from tdsurface.las.forms import *

LASNULL = '-9999'

def las_test(request) :
    """Generates a test LAS file from test data"""
    curve_header = CurveHeader([
        Descriptor(mnemonic="DEPT", unit="m", description="DEPTH"),
        #Descriptor(mnemonic="NetGross", description="NetGross"),
        #Descriptor(mnemonic="Facies", description="Facies"),
        #Descriptor(mnemonic="Porosity", unit="m3/m3", description="Gamma"),
        Descriptor(mnemonic="GAMMA", unit="gAPI", description="Gamma"),
        Descriptor(mnemonic="DEPTH", unit="m", description="trend")
        ])

    well_header = WellHeader([
        Descriptor(mnemonic="STRT", unit="m", data="100"),
        Descriptor(mnemonic="STOP", unit="m", data="1000"),
        Descriptor(mnemonic="STEP", unit="m", data="0"),
        Descriptor(mnemonic="COMP", description="COMPANY"),
        Descriptor(mnemonic="DATE", data=date.today().isoformat(), description="Log Date")])

    parameter_header = ParameterHeader([])

    depth_curve = LasCurve(Descriptor("DEPT", "m", None, "DEPTH"), range(100,1000,100))
    gama_curve = LasCurve(Descriptor("DEPT", "m", None, "DEPTH"), range(10,100,10))
    
    lf = LasFile(VersionHeader("2.0", False), well_header, curve_header, parameter_header, [depth_curve, gama_curve, depth_curve])

    
    return HttpResponse(lf.to_las(), mimetype="text/plain")


def las_from_mwdlog(request, object_id) :
    """Generates a LAS file of the MWD Log for a given run"""

    run = Run.objects.get(pk=object_id)
    if request.method == 'POST': # If the form has been submitted...
        form = LasFromMWDLogForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass    
            

            mwdlog = ToolMWDLog.objects.filter(well=run.well_bore.well, time_stamp__gte=run.start_time, time_stamp__lte=run.end_time, depth__gt=0).order_by('depth')

            mwdlog_agg = ToolMWDLog.objects.filter(well=run.well_bore.well, time_stamp__gte=run.start_time, time_stamp__lte=run.end_time, depth__gt=0).aggregate(Min('depth'), Max('depth'))
            well_headers = [
                Descriptor(mnemonic="STRT", unit="FT", data=str(mwdlog_agg['depth__min'])),
                Descriptor(mnemonic="STOP", unit="FT", data=str(mwdlog_agg['depth__max'])),
                Descriptor(mnemonic="STEP", unit="S", data="0"),
                Descriptor(mnemonic="NULL", data = LASNULL, description="Null Value"),
                Descriptor(mnemonic="COMP", data=run.well_bore.well.operator, description="Company"),
                Descriptor(mnemonic="WELL", data=run.well_bore.well.name, description="Well Name"),
                Descriptor(mnemonic="FLD", data=run.well_bore.well.field, description="Field Name"),
                Descriptor(mnemonic="LOC", data=' ', description="Location"),
                Descriptor(mnemonic="CNTY", data=run.well_bore.well.county, description="County"),
                Descriptor(mnemonic="STAT", data=run.well_bore.well.state, description="State"),
                Descriptor(mnemonic="CTRY", data=run.well_bore.well.country, description="Country"),
                Descriptor(mnemonic="SRVC", data="TeleDrill", description="Service Company"),
                Descriptor(mnemonic="API", data=run.well_bore.well.api_number, description="API Number"),
                Descriptor(mnemonic="RUN", data=str(run).replace(':',' '), description="Run Name"),
                Descriptor(mnemonic="RUNID", data=run.pk, description="Run Id"),
                Descriptor(mnemonic="DATE", data=run.start_time.date().isoformat(), description="Log Start Date")
                ]

            curve_headers = [Descriptor(mnemonic="DEPT", unit="ft", description="Bit Depth"),]
            curves = [LasCurve(Descriptor(mnemonic="DEPT", unit="ft", description="Bit Depth"), [l.depth for l in mwdlog])]

            if form.cleaned_data['elapsed_time'] :
                d = Descriptor(mnemonic="ETIM", unit="S", description="Elapsed Time")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.seconds for l in mwdlog]))
                
            if form.cleaned_data['status'] :
                d = Descriptor(mnemonic="STAT", unit="", description="Tool Status")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.status for l in mwdlog])) 

            if form.cleaned_data['temperature_f'] :
                d = Descriptor(mnemonic="TMP", unit="degF", description="Temperature")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.temperature_f() for l in mwdlog]))

            if form.cleaned_data['temperature_c'] :
                d = Descriptor(mnemonic="TMP", unit="degC", description="Temperature")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.temperature_c() for l in mwdlog]))
                           
            
            if form.cleaned_data['gravity_x'] or form.cleaned_data['total_gravity'] :                
                gravity_x_calibrated = [l.gravity_x_calibrated(run) for l in mwdlog]                

            if form.cleaned_data['gravity_y'] or form.cleaned_data['total_gravity'] :
                gravity_y_calibrated = [l.gravity_y_calibrated(run) for l in mwdlog]                

            if form.cleaned_data['gravity_z'] or form.cleaned_data['total_gravity'] :
                gravity_z_calibrated = [l.gravity_z_calibrated(run) for l in mwdlog]                

            if form.cleaned_data['gravity_x'] :
                d = Descriptor(mnemonic="GX", unit="", description="Gravity x calibrated")
                curve_headers.append(d)
                curves.append(LasCurve(d,gravity_x_calibrated))  

            if form.cleaned_data['gravity_y'] :
                d = Descriptor(mnemonic="GYY", unit="", description="Gravity y calibrated")
                curve_headers.append(d)
                curves.append(LasCurve(d,gravity_y_calibrated))  

            if form.cleaned_data['gravity_z'] :
                d = Descriptor(mnemonic="GZ", unit="", description="Gravity z calibrated")
                curve_headers.append(d)
                curves.append(LasCurve(d,gravity_z_calibrated))  

            # total is the root of the sum of the squares of x, y, & z
            if form.cleaned_data['total_gravity'] :
                d = Descriptor(mnemonic="GT", unit="", description="Total Gravity")
                curve_headers.append(d)                
                #curves.append(LasCurve(d,[round(sqrt(pow(gravity_x_calibrated[c],2)+pow(gravity_y_calibrated[c],2)+pow(gravity_z_calibrated[c],2)),3) for c in range(len(mwdlog))]))
                curves.append(LasCurve(d,[ l.total_gravity(run) for l in mwdlog]))
            
            if form.cleaned_data['magnetic_x'] or form.cleaned_data['total_magnetic'] :                
                magnetic_x_calibrated = [l.magnetic_x_calibrated(run) for l in mwdlog]

            if form.cleaned_data['magnetic_y'] or form.cleaned_data['total_magnetic'] :
                magnetic_y_calibrated = [l.magnetic_y_calibrated(run) for l in mwdlog]

            if form.cleaned_data['magnetic_z'] or form.cleaned_data['total_magnetic'] :
                magnetic_z_calibrated = [l.magnetic_z_calibrated(run) for l in mwdlog]

            if form.cleaned_data['magnetic_x'] :
                d = Descriptor(mnemonic="HX", unit="mT", description="Magnetic x calibrated")
                curve_headers.append(d)
                curves.append(LasCurve(d,magnetic_x_calibrated))  

            if form.cleaned_data['magnetic_y'] :
                d = Descriptor(mnemonic="HY", unit="mT", description="Magnetic y calibrated")
                curve_headers.append(d)
                curves.append(LasCurve(d,magnetic_y_calibrated))  

            if form.cleaned_data['magnetic_z'] :
                d = Descriptor(mnemonic="HZ", unit="mT", description="Magnetic z calibrated")
                curve_headers.append(d)
                curves.append(LasCurve(d,magnetic_z_calibrated))  

            # total is the root of the sum of the squares of x, y, & z
            if form.cleaned_data['total_magnetic'] :
                d = Descriptor(mnemonic="HT", unit="", description="Total Magnetic")
                curve_headers.append(d)                
                #curves.append(LasCurve(d,[round(sqrt(pow(magnetic_x_calibrated[c],2)+pow(magnetic_y_calibrated[c],2)+pow(magnetic_z_calibrated[c],2)),3) for c in range(len(mwdlog))]))
                curves.append(LasCurve(d,[ l.total_magnetic(run) for l in mwdlog ]))


            
            lf = LasFile(VersionHeader("2.0", False), WellHeader(well_headers), CurveHeader(curve_headers), ParameterHeader([]), curves)

            return HttpResponse(lf.to_las(), mimetype="text/plain")

    else:
        form = LasFromMWDLogForm() # An unbound form

    rtform = LasFromRTLogForm()
    gammaform = LasFromMWDGammaLogForm()
    return render_to_response('las_from_mwdlog_form.html', {'gammaform': gammaform, 'mwdform': form, 'rtform': rtform, 'object': run, 'run':run, 'navigation_template': 'run_detail_menu.html'}, context_instance = RequestContext(request))    



def las_from_mwdgammalog(request, object_id) :
    """Generates a LAS file of the MWD Gamma Log for a given run"""

    run = Run.objects.get(pk=object_id)
    if request.method == 'POST': # If the form has been submitted...
        form = LasFromMWDGammaLogForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass    
            

            log = ToolMWDLogGamma.objects.filter(run=run, depth__gt=0).order_by('depth')

            log_agg = ToolMWDLogGamma.objects.filter(run=run, depth__gt=0).aggregate(Min('depth'), Max('depth'))
            well_headers = [
                Descriptor(mnemonic="STRT", unit="FT", data=str(log_agg['depth__min'])),
                Descriptor(mnemonic="STOP", unit="FT", data=str(log_agg['depth__max'])),
                Descriptor(mnemonic="STEP", unit="S", data="0"),
                Descriptor(mnemonic="NULL", data = LASNULL, description="Null Value"),
                Descriptor(mnemonic="COMP", data=run.well_bore.well.operator, description="Company"),
                Descriptor(mnemonic="WELL", data=run.well_bore.well.name, description="Well Name"),
                Descriptor(mnemonic="FLD", data=run.well_bore.well.field, description="Field Name"),
                Descriptor(mnemonic="LOC", data=' ', description="Location"),
                Descriptor(mnemonic="CNTY", data=run.well_bore.well.county, description="County"),
                Descriptor(mnemonic="STAT", data=run.well_bore.well.state, description="State"),
                Descriptor(mnemonic="CTRY", data=run.well_bore.well.country, description="Country"),
                Descriptor(mnemonic="SRVC", data="TeleDrill", description="Service Company"),
                Descriptor(mnemonic="API", data=run.well_bore.well.api_number, description="API Number"),
                Descriptor(mnemonic="RUN", data=str(run).replace(':',' '), description="Run Name"),
                Descriptor(mnemonic="RUNID", data=run.pk, description="Run Id"),
                Descriptor(mnemonic="DATE", data=run.start_time.date().isoformat(), description="Log Start Date")
                ]

            curve_headers = [Descriptor(mnemonic="DEPT", unit="ft", description="Bit Depth"),]
            curves = [LasCurve(Descriptor(mnemonic="DEPT", unit="ft", description="Bit Depth"), [l.depth for l in log])]

            if form.cleaned_data['elapsed_time'] :
                d = Descriptor(mnemonic="ETIM", unit="S", description="Elapsed Time")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.seconds for l in log]))
                
            if form.cleaned_data['status'] :
                d = Descriptor(mnemonic="STAT", unit="", description="Tool Status")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.status for l in log]))             
                
            if form.cleaned_data['gamma_ray'] :
                d = Descriptor(mnemonic="GR", unit="CPS", description="Gamma Ray counts/second")
                curve_headers.append(d)
                curves.append(LasCurve(d,['%.1f' % round((pow(10, l.gamma*2/10000.0 ) * 2),1)  for l in log]))
            
            
            
            lf = LasFile(VersionHeader("2.0", False), WellHeader(well_headers), CurveHeader(curve_headers), ParameterHeader([]), curves)

            return HttpResponse(lf.to_las(), mimetype="text/plain")

    else:
        form = LasFromMWDGammaLogForm() # An unbound form

    rtform = LasFromRTLogForm()
    mwdform = LasFromMWDLogForm()
    return render_to_response('las_from_mwdlog_form.html', {'gammaform':form, 'mwdform': mwdform, 'rtform': rtform, 'object': run, 'run':run, 'navigation_template': 'run_detail_menu.html'}, context_instance = RequestContext(request))    


def las_from_rtlog(request, object_id) :
    """Generates a LAS file of the Real Time Log for a given run"""

    run = Run.objects.get(pk=object_id)
    if request.method == 'POST': # If the form has been submitted...
        form = LasFromRTLogForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass    
            
            type = []
        
            rtlog = ToolMWDRealTime.objects.filter(well=run.well_bore.well, time_stamp__gte=run.start_time, time_stamp__lte=run.end_time, depth__gt=0).order_by('depth')

            rtlog_agg = ToolMWDRealTime.objects.filter(well=run.well_bore.well, time_stamp__gte=run.start_time, time_stamp__lte=run.end_time, depth__gt=0).aggregate(Min('depth'), Max('depth'))
            well_headers = [
                Descriptor(mnemonic="STRT", unit="FT", data=str(rtlog_agg['depth__min'])),
                Descriptor(mnemonic="STOP", unit="FT", data=str(rtlog_agg['depth__max'])),
                Descriptor(mnemonic="STEP", unit="S", data="0"),
                Descriptor(mnemonic="NULL", data = LASNULL, description="Null Value"),
                Descriptor(mnemonic="COMP", data=run.well_bore.well.operator, description="Company"),
                Descriptor(mnemonic="WELL", data=run.well_bore.well.name, description="Well Name"),
                Descriptor(mnemonic="FLD", data=run.well_bore.well.field, description="Field Name"),
                Descriptor(mnemonic="LOC", data=' ', description="Location"),
                Descriptor(mnemonic="CNTY", data=run.well_bore.well.county, description="County"),
                Descriptor(mnemonic="STAT", data=run.well_bore.well.state, description="State"),
                Descriptor(mnemonic="CTRY", data=run.well_bore.well.country, description="Country"),
                Descriptor(mnemonic="SRVC", data="TeleDrill", description="Service Company"),
                Descriptor(mnemonic="API", data=run.well_bore.well.api_number, description="API Number"),
                Descriptor(mnemonic="RUN", data=str(run).replace(':',' '), description="Run Name"),
                Descriptor(mnemonic="RUNID", data=run.pk, description="Run Id"),
                Descriptor(mnemonic="DATE", data=run.start_time.date().isoformat(), description="Log Start Date")
                ]

            curves = [LasCurve(Descriptor(mnemonic="DEPT", unit="ft", description="Bit Depth"), [])]
            curve_headers = [Descriptor(mnemonic="DEPT", unit="ft", description="Bit Depth"),]
                
            if form.cleaned_data['status'] :
                d = Descriptor(mnemonic="STAT", unit="", description="Tool Status")
                curve_headers.append(d)
                curves.append(LasCurve(d,[])) 
                type.append('status')
                
            if form.cleaned_data['temperature_f'] :
                d = Descriptor(mnemonic="TMP", unit="degF", description="Temperature")
                curve_headers.append(d)
                curves.append(LasCurve(d,[]))
                type.append('temperature')
                
            if form.cleaned_data['gamma_ray'] :
                d = Descriptor(mnemonic="GR", unit="CPS", description="Gamma Ray counts/second")
                curve_headers.append(d)
                curves.append(LasCurve(d,[]))
                type.append('gammaray')
                                    
            if form.cleaned_data['gravity'] :
                d = Descriptor(mnemonic="GT", unit="", description="Total Gravity")
                curve_headers.append(d)                                
                curves.append(LasCurve(d,[]))
                type.append('g')
                        
            if form.cleaned_data['magnetic'] :
                d = Descriptor(mnemonic="HT", unit="", description="Total Magnetic")
                curve_headers.append(d)                                
                curves.append(LasCurve(d,[]))
                type.append('H')

            if form.cleaned_data['azimuth'] :
                d = Descriptor(mnemonic="AZI", unit="DEG", description="Azimuth")
                curve_headers.append(d)                                
                curves.append(LasCurve(d,[]))
                type.append('azimuth')

            if form.cleaned_data['inclination'] :
                d = Descriptor(mnemonic="INCL", unit="DEG", description="Inclination")
                curve_headers.append(d)                                
                curves.append(LasCurve(d,[]))
                type.append('inclination')

            if form.cleaned_data['tool_face'] :
                d = Descriptor(mnemonic="TF", unit="DEG", description="Tool Face")
                curve_headers.append(d)                                
                curves.append(LasCurve(d,[]))
                type.append('toolface')

                        
            data = {}    
            for l in rtlog :
                data.setdefault(l.depth,{}).setdefault(l.type,[]).append(float(l.value))

            l = data.items()
            l.sort()
            for k,v in l :
                curves[0].data.append(k)
                for c in curves[1:] :
                    if c.descriptor.mnemonic == 'AZI' :
                        vl = v.get('azimuth',(LASNULL,))                        
                                                
                    if c.descriptor.mnemonic == 'INCL' :                        
                        vl = v.get('inlination',(LASNULL,))                                                
                        
                    if c.descriptor.mnemonic == 'TF' :                        
                        vl = v.get('toolface',(LASNULL,))                                                
                        
                    if c.descriptor.mnemonic == 'STAT' :                        
                        vl = v.get('status',(LASNULL,))                                                
                        
                    if c.descriptor.mnemonic == 'TMP' :                        
                        vl = v.get('temperature',(LASNULL,))                                                
                        
                    if c.descriptor.mnemonic == 'GR' :                        
                        vl = v.get('gammaray',(LASNULL,))                                                
                        
                    if c.descriptor.mnemonic == 'GT' :                        
                        vl = v.get('g',(LASNULL,))                                                
                        
                    if c.descriptor.mnemonic == 'HT' :                        
                        vl = v.get('H',(LASNULL,))                                                

                    if len(vl)>1 :
                        c.data.append(sum(vl)/len(vl))
                    else :
                        c.data.append(vl[0])
                                                    
            lf = LasFile(VersionHeader("2.0", False), WellHeader(well_headers), CurveHeader(curve_headers), ParameterHeader([]), curves)

            return HttpResponse(lf.to_las(), mimetype="text/plain")

    else:
        logform = LasFromMWDLogForm() # An unbound form

    mwdform = LasFromMWDLogForm()
    gammaform = LasFromMWDGammaLogForm()
    
    return render_to_response('las_from_mwdlog_form.html', {'gammaform': gammaform, 'mwdform': mwdform, 'rtform': form, 'object': run, 'run':run, 'navigation_template': 'run_detail_menu.html'}, context_instance = RequestContext(request))    
