from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import Http404
from django.template import loader, Context
from django.template import RequestContext 
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from tdsurface.shortcuts import get_object_or_None

from tdsurface.bha.models import Run
from tdsurface.bha.models import *
from tdsurface.bha.forms import *

from django.utils import simplejson

def bha_update(request, object_id, extra_context=None) :

    run = Run.objects.get(pk=object_id)

    bha = get_object_or_None(BHA, run=run)
    if not bha :
        bha = BHA(run=run)
        bha.save()
        
    if request.method == 'POST':
        bha_form = BHAForm(request.POST, instance=bha) # A form bound to the POST data
        if bha_form.is_valid(): # All validation rules pass
            bha_form.save()            
            return HttpResponseRedirect(reverse('bha_update', args=[object_id]))

    else :
        bha_form = BHAForm(instance=bha)
        
    data = {'object': run, 'bha_form': bha_form, 'bha':bha}
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    

    return render_to_response('bha_update_form.html', data, context_instance = RequestContext(request))


def bha_component_grid(request, object_id) :

    run = Run.objects.get(pk=object_id)
    bha = BHA.objects.get(run=run)

    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    
    sort_order= ''
    if request.GET['sord'] == 'desc' :
        sort_order= '-'
    
    cs = Component.objects.filter(bha=bha).order_by(sort_order+request.GET['sidx'])
    records = len(cs)
    total_pages = records/rows;
    if records % rows :
        total_pages += 1
        
    data={
        'total': total_pages,
        'page': page,
        'records': records,
        'rows' : [ ],
        }

    for r in cs[(page-1)*rows:page*rows] :
        rd = {}
        rd["id"] = r.pk        
        rd['order'] = str(r.order)        
        rd['description'] = r.description
        rd['serial_number'] = r.serial_number        
        rd['odia'] = str(r.odia)
        rd['idia'] = str(r.idia)
        rd['fn_length'] = str(r.fn_length)
        rd['top_conn'] = r.top_conn
        rd['pb'] = r.pb
        rd['length'] = str(r.length)
        
        
        data['rows'].append(rd)

    data = simplejson.dumps(data)       
    return HttpResponse(data, mimetype="application/javascript")

        
def bha_component_grid_edit(request, object_id) :    

    run = Run.objects.get(pk=object_id)
    bha = BHA.objects.get(run=run)
    
    if request.method=='POST' :
        if request.POST['id'] == 'new' :
            order = request.POST['order']
            if order == 'end' :
                order = 9999
            order = int(order)
            print 'we got here'               
            c = Component(bha=bha,
                           order = order,
                           description = request.POST['description'],
                           serial_number = request.POST['serial_number'],
                           odia = request.POST['odia'],
                           idia = request.POST['idia'],
                           fn_length = request.POST['fn_length'],
                           top_conn = request.POST['top_conn'],
                           pb = request.POST['pb'],                           
                           length = request.POST['length']
                           )            
            print 'how bout here'
            cs = Component.objects.filter(bha=bha).order_by('order')
            max_order = 0
            for x in cs :
                if x.order >= c.order :
                    x.order += 1                
                    x.save()
                if x.order > max_order :
                    max_order = x.order            

            if c.order >= max_order :
                c.order = max_order + 1
            c.save()    
            
        else :            
            c = Component.objects.get(pk = request.POST['id'])            
            order = int(request.POST['order'])
            if c.order != order :
                cs = Component.objects.filter(order = order)
                if len(cs) :
                    cs[0].order = c.order
                    cs[0].save()                
            c.order = order
            c.description = request.POST['description']
            c.serial_number = request.POST['serial_number']
            c.odia = request.POST['odia']
            c.idia = request.POST['idia']
            c.fn_length = request.POST['fn_length']
            c.top_conn = request.POST['top_conn']
            c.pb = request.POST['pb']                       
            c.length = request.POST['length']
            c.save()                
        
            
    data = simplejson.dumps(c.pk)       
    return HttpResponse(data, mimetype="application/javascript")                
    

def bha_component_grid_delete(request, object_id) :    

    run = Run.objects.get(pk=object_id)
    bha = BHA.objects.get(run=run)
    
    if request.method=='POST' :        
        c = Component.objects.get(pk = request.POST['id'])
        order = c.order
        c.delete()
        cs = Component.objects.filter(bha=bha).order_by('order')
        for x in range(len(cs)) :            
            if cs[x].order != x + 1 :
                cs[x].order = x + 1
                cs[x].save()
            
        return HttpResponse('true', mimetype="application/javascript")            
