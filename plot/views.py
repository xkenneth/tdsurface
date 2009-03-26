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
import matplotlib.text as text
from datetime import datetime
from datetime import timedelta
from time import mktime
from django.db.models import Avg, Max, Min, Count
from django.shortcuts import render_to_response

def plot_realtime_gammaray(request, object_id) :

    run = Run.objects.get(pk=object_id)
    
    x1 = []
    x2 = []
    y = []

    hoursago = datetime.utcnow() - timedelta(hours=12)
    r = ToolMWDRealTime.objects.filter(run=run, type='gammaray', value__gt=0, value__lt=500, time_stamp__gt=hoursago).order_by('-time_stamp')
    ragg = ToolMWDRealTime.objects.filter(run=run, type='gammaray', value__gt=0, value__lt=500, time_stamp__gt=hoursago).aggregate(Min('time_stamp'), Max('time_stamp'))

    interval=5

    # System goes to 100% memory used 0-1 points are plotted
    if len(r) < 2 :
        return render_to_response('message.html', {'message': 'No Data to graph'})
    
    delta = ragg['time_stamp__max'] - ragg['time_stamp__min']
    minutes = (delta.seconds+(delta.days*24*60*60))/60
    interval = max(minutes/10,interval)    
    #print '%d:%d' % (minutes, interval)
    
    [x1.append(v.value) for v in r]    
    [y.append(v.time_stamp) for v in r]    

    for l in r :
        if l.depth != None :
            x2.append(l.depth)
            continue
        time_stamp = l.time_stamp
        try :            
            lower = WITS0.objects.filter(run=run, recid=1, itemid=8, time_stamp__lt = time_stamp ).order_by('-time_stamp')[0]
            higher = WITS0.objects.filter(run=run, recid=1, itemid=8, time_stamp__gt = time_stamp ).order_by('time_stamp')[0]
        except:
            x2.append(0)
            continue

        # Linear Interpolation where x = seconds and y = depth    
        x = mktime(time_stamp.timetuple())
        xa = mktime(lower.time_stamp.timetuple())
        xb = mktime(higher.time_stamp.timetuple())

        ya = float(lower.value)
        yb = float(higher.value)
        
        depth = ya + ((x - xa) * (yb - ya))/(xb - xa)

        l.depth=str(depth)
        l.depth_units='ft'
        l.save()
        x2.append(l.depth)

    fig = Figure()
    canvas = FigureCanvas(fig)
    #ax = fig.add_subplot(111)
    #ax = fig.add_axes([0.23, 0.08 ,0.7 ,0.87])
    ax = fig.add_axes([0.23, 0.08 ,0.7 ,0.85])
    ax.plot(x1, y, 'r')
    #ax.set_title('Gamma Ray')
    ax.grid(True)
    ax.set_xlabel('Gamma Ray (counts/sec)', color='r')
    ax.set_ylabel('time (UTC)')    
    formatter = dates.DateFormatter('%H:%M') 
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator( MinuteLocator( interval=interval ) )
    ax.xaxis.set_major_locator( LinearLocator( numticks=5 ) )
    
    for tl in ax.get_xticklabels():
        tl.set_color('r')

    ax2 = ax.twiny()
    ax2.set_xlabel('Depth (ft)', color='b')
    ax2.plot(x2, y, 'b')
    ax2.yaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_locator( MinuteLocator( interval=interval ) )
    ax2.xaxis.set_major_locator( LinearLocator( numticks=5 ) )

    for tl in ax2.get_xticklabels():
        tl.set_color('b')
    
    fontsize=8
    #for tick in ax.xaxis.get_major_ticks():
    #    tick.label1.set_fontsize(fontsize)
    #for tick in ax.yaxis.get_major_ticks():
    #    tick.label1.set_fontsize(fontsize)

    for o in fig.findobj(text.Text) :
        o.set_fontsize(8)

    #fig.subplots_adjust(left=0.25)
    fig.autofmt_xdate()
    fig.set_size_inches( (2.5, 5) )
        
    filename = settings.MEDIA_ROOT + '/images/gammaray_rt.png'
    fig.savefig(filename)
     
    #data = simplejson.dumps({'filename': filename})       
    #return HttpResponse(data, mimetype="application/javascript")
    return HttpResponseRedirect('/tdsurface/media/images/gammaray_rt.png')
