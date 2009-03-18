from tdsurface.depth.models import *

import matplotlib
matplotlib.use("Agg") # do this before pylab so you don'tget the default back end.

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
    pylab
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

