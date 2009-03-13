from django.http import HttpResponse
from django.template import loader, Context
from django.template import RequestContext 
from django.shortcuts import render_to_response
from django.db.models import Avg, Max, Min, Count

from las.file import *
from las.headers import *
from datetime import date, datetime

from tdsurface.depth.models import ToolMWDLog
from tdsurface.depth.models import Run
from tdsurface.las.forms import *

from math import sqrt

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
            

            mwdlog = ToolMWDLog.objects.filter(run=object_id, seconds__lt=200000000).order_by('seconds')

            mwdlog_agg = ToolMWDLog.objects.filter(run=object_id, seconds__lt=200000000).aggregate(Min('seconds'), Max('seconds'))
            well_headers = [
                Descriptor(mnemonic="STRT", unit="S", data=str(mwdlog_agg['seconds__min'])),
                Descriptor(mnemonic="STOP", unit="S", data=str(mwdlog_agg['seconds__max'])),
                Descriptor(mnemonic="STEP", unit="S", data="0"),
                Descriptor(mnemonic="NULL", data = "9999", description="Null Value"),
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

            curve_headers = [Descriptor(mnemonic="ETIM", unit="S", description="Elapsed Time"),]
            curves = [LasCurve(Descriptor(mnemonic="ETIM", unit="S", description="Elapsed Time"), [l.seconds for l in mwdlog])]

            if form.cleaned_data['status'] :
                d = Descriptor(mnemonic="STAT", unit="", description="Tool Status")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.status for l in mwdlog])) 

            if form.cleaned_data['temperature'] :
                d = Descriptor(mnemonic="TMP", unit="degF", description="Temperature")
                curve_headers.append(d)
                curves.append(LasCurve(d,[l.temperature*500/10000.0 for l in mwdlog]))                 
            
            if form.cleaned_data['gamma_ray_0'] :
                d = Descriptor(mnemonic="GR0", unit="CPS", description="Gamma Rate counts/second first quarter logging cycle")
                curve_headers.append(d)
                curves.append(LasCurve(d,['%.1f' % round((pow(10, l.gamma0*2/10000.0 ) * 2),1)  for l in mwdlog]))
            
            if form.cleaned_data['gamma_ray_1'] :
                d = Descriptor(mnemonic="GR1", unit="CPS", description="Gamma Ray counts/second second quarter logging cycle")
                curve_headers.append(d)
                curves.append(LasCurve(d,['%.1f' % round((pow(10, l.gamma1*2/10000.0 ) * 2),1)  for l in mwdlog]))

            if form.cleaned_data['gamma_ray_2'] :
                d = Descriptor(mnemonic="GR2", unit="CPS", description="Gamma Ray counts/second third quarter logging cycle")
                curve_headers.append(d)
                curves.append(LasCurve(d,['%.1f' % round((pow(10, l.gamma2*2/10000.0 ) * 2),1)  for l in mwdlog]))

            if form.cleaned_data['gamma_ray_3'] :
                d = Descriptor(mnemonic="GR3", unit="CPS", description="Gamma counts/second forth quarter logging cycle")
                curve_headers.append(d)
                curves.append(LasCurve(d,['%.1f' % round((pow(10, l.gamma3*2/10000.0 ) * 2),1)  for l in mwdlog]))

            #Apply calibration contants
            if form.cleaned_data['gravity_x'] or form.cleaned_data['total_gravity'] :
                gravity_x_calibrated = [round((l.gravity_x-run.tool_calibration.accelerometer_x_offset)/(1.0*run.tool_calibration.accelerometer_x_gain),3) for l in mwdlog]

            if form.cleaned_data['gravity_y'] or form.cleaned_data['total_gravity'] :
                gravity_y_calibrated = [round((l.gravity_y-run.tool_calibration.accelerometer_y_offset)/(1.0*run.tool_calibration.accelerometer_y_gain),3) for l in mwdlog]

            if form.cleaned_data['gravity_y'] or form.cleaned_data['total_gravity'] :
                gravity_z_calibrated = [round((l.gravity_z-run.tool_calibration.accelerometer_z_offset)/(1.0*run.tool_calibration.accelerometer_z_gain),3) for l in mwdlog]

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
                curves.append(LasCurve(d,[round(sqrt(pow(gravity_x_calibrated[c],2)+pow(gravity_y_calibrated[c],2)+pow(gravity_z_calibrated[c],2)),3) for c in range(len(mwdlog))]))  

            #Apply calibration contants
            if form.cleaned_data['magnetic_x'] or form.cleaned_data['total_magnetic'] :
                magnetic_x_calibrated = [round((l.magnetic_x-run.tool_calibration.accelerometer_x_offset)/(1.0*run.tool_calibration.accelerometer_x_gain),3) for l in mwdlog]

            if form.cleaned_data['magnetic_y'] or form.cleaned_data['total_magnetic'] :
                magnetic_y_calibrated = [round((l.magnetic_y-run.tool_calibration.accelerometer_y_offset)/(1.0*run.tool_calibration.accelerometer_y_gain),3) for l in mwdlog]

            if form.cleaned_data['magnetic_y'] or form.cleaned_data['total_magnetic'] :
                magnetic_z_calibrated = [round((l.magnetic_z-run.tool_calibration.accelerometer_z_offset)/(1.0*run.tool_calibration.accelerometer_z_gain),3) for l in mwdlog]

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
                curves.append(LasCurve(d,[round(sqrt(pow(magnetic_x_calibrated[c],2)+pow(magnetic_y_calibrated[c],2)+pow(magnetic_z_calibrated[c],2)),3) for c in range(len(mwdlog))]))  


            
            lf = LasFile(VersionHeader("2.0", False), WellHeader(well_headers), CurveHeader(curve_headers), ParameterHeader([]), curves)

            return HttpResponse(lf.to_las(), mimetype="text/plain")

    else:
        form = LasFromMWDLogForm() # An unbound form

    return render_to_response('las_from_mwdlog_form.html', {'form': form, 'object_id': object_id, 'run':run }, context_instance = RequestContext(request))    
