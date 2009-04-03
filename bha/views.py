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
        
    data = {'object': run, 'bha_form': bha_form}
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    

    return render_to_response('bha_update_form.html', data, context_instance = RequestContext(request))
