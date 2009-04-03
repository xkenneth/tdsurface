from tdsurface.depth.models import *
from django.conf import settings
from django.http import HttpResponseRedirect

import matplotlib
matplotlib.use("Agg") # do this before pylab so you don't get the default back end.

import pylab
import matplotlib.numerix as N

from django.utils import simplejson

def test_matplotlib(request) :
    # Generate and plot some simple data:
    x = N.arange(0, 2*N.pi, 0.1)
    y = N.sin(x)+1

    pylab.ylim(8,0)
    pylab.plot(y,x)
    F = pylab.gcf()

    # Now check everything with the defaults:
    DPI = F.get_dpi()    
    DefaultSize = F.get_size_inches()
    F.set_size_inches( (2, 5) )
    filename = settings.MEDIA_ROOT + '/images/test1.png'
    F.savefig(filename)
     
    data = simplejson.dumps({'filename': filename})   
    
    return HttpResponse(data, mimetype="application/javascript")

def test_matplotlib_weight_on_bit(request) :
    x = []
    y = []
    
    r = WITS0.objects.filter(recid=1,itemid=17, value__gt=0).order_by('-time_stamp')[:300]
        
    [x.append(v.value) for v in r]
    [y.append(v.time_stamp) for v in r]

    pylab.ylim(10,0)
    #pylab.xlim(0,40)
    pylab.grid(True)
    pylab.plot(x,y)    
    F = pylab.gcf()

    # Now check everything with the defaults:
    DPI = F.get_dpi()    
    #DefaultSize = F.get_size_inches()
    F.set_size_inches( (2, 5) )
    filename = settings.MEDIA_ROOT + '/images/test1.png'
    F.savefig(filename)
     
    data = simplejson.dumps({'filename': filename})   
    
    #return HttpResponse(data, mimetype="application/javascript")
    return HttpResponseRedirect('/tdsurface/media/images/test1.png')


from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import dates
from matplotlib.dates import HourLocator, MinuteLocator
from matplotlib.ticker import LinearLocator
from matplotlib.ticker import FuncFormatter
import matplotlib.text as text
from datetime import datetime
from datetime import timedelta
from time import mktime
from django.db.models import Avg, Max, Min, Count
from django.shortcuts import render_to_response
import pytz

def plot_realtime_gammaray(request, object_id) :

    run = Run.objects.get(pk=object_id)
    wltz = pytz.timezone(run.well_bore.well.timezone)
    gammas = []    
    times = []

    ragg = ToolMWDRealTime.objects.filter(run=run, type='gammaray').aggregate(Max('time_stamp'))
    hoursago = (ragg['time_stamp__max'] or datetime.utcnow()) - timedelta(hours=1)
    r = ToolMWDRealTime.objects.filter(run=run, type='gammaray', time_stamp__gt=hoursago).order_by('time_stamp')    

    # System goes to 100% memory used if 0-1 points are plotted
    if len(r) < 2 :
        return render_to_response('message.html', {'message': 'No Data to graph'})
    
    [gammas.append(v.value) for v in r]    
    [times.append(v.time_stamp) for v in r]    

    def depth_formatter(time_stamp, arg2) :
        time_stamp = matplotlib.dates.num2date(time_stamp)
        time_stamp = time_stamp.replace(tzinfo=None)
        wlt = pytz.utc.localize(time_stamp).astimezone(wltz).replace(tzinfo=None)
        ftime = wlt.strftime('%H:%M')
        
        try :            
            lower = WITS0.objects.filter(run=run, recid=1, itemid=8, time_stamp__lt = time_stamp ).order_by('-time_stamp')[0]
            higher = WITS0.objects.filter(run=run, recid=1, itemid=8, time_stamp__gt = time_stamp ).order_by('time_stamp')[0]
        except:            
            return '%s / No Dpth' % ftime

        # Linear Interpolation where x = seconds and y = depth    
        x = mktime(time_stamp.timetuple())
        xa = mktime(lower.time_stamp.timetuple())
        xb = mktime(higher.time_stamp.timetuple())

        ya = float(lower.value)
        yb = float(higher.value)
        
        depth = ya + ((x - xa) * (yb - ya))/(xb - xa)
        
        return '%s / %s' % (ftime, str(int(depth)) )

    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_axes([0.4, 0.08 ,0.55 ,0.85])
    ax.plot(gammas, times)
    ax.set_title('Gamma Ray')
    ax.grid(True)
    ax.set_xlabel('Gamma Ray (counts/sec)')
    ax.set_ylabel('Time / Depth (ft)')    
    formatter = dates.DateFormatter('%H:%M') 
    ax.yaxis.set_major_formatter(FuncFormatter(depth_formatter))
    ax.set_ylim(matplotlib.dates.date2num(times[-1]),matplotlib.dates.date2num(times[0]))
    ax.yaxis.set_major_locator( LinearLocator( numticks=10 ) )
    ax.xaxis.set_major_locator( LinearLocator( numticks=5 ) )

    going_down = True
    prev_depth = -999
    for t in times :
        try :            
            lower = WITS0.objects.filter(run=run, recid=1, itemid=8, time_stamp__lt = t ).order_by('-time_stamp')[0]
            higher = WITS0.objects.filter(run=run, recid=1, itemid=8, time_stamp__gt = t ).order_by('time_stamp')[0]
        except:            
            continue

        # Linear Interpolation where x = seconds and y = depth    
        x = mktime(t.timetuple())
        xa = mktime(lower.time_stamp.timetuple())
        xb = mktime(higher.time_stamp.timetuple())

        ya = float(lower.value)
        yb = float(higher.value)
        
        depth = ya + ((x - xa) * (yb - ya))/(xb - xa)
        #print depth, going_down
        if depth < prev_depth :
            if going_down :
                going_down=False
                t1 = t

        if depth >= prev_depth and not going_down :
            going_down=True
            t2 = t                        
            ax.axhspan(matplotlib.dates.date2num(t1), matplotlib.dates.date2num(t2), facecolor='#FF0033', alpha=0.25)

        prev_depth = depth

    if not going_down :
        ax.axhspan(matplotlib.dates.date2num(t1), matplotlib.dates.date2num(times[-1]), facecolor='#FF0033', alpha=0.25)
    
    fontsize=8

    for o in fig.findobj(text.Text) :
        o.set_fontsize(fontsize)
    
    fig.set_size_inches( (3, 5) )
        
    filename = settings.MEDIA_ROOT + '/images/gammaray_rt.png'
    fig.savefig(filename)
         
    return HttpResponseRedirect('/tdsurface/media/images/gammaray_rt.png')
