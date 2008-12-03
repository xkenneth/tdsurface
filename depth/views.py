from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from tdsurface.shortcuts import get_object_or_None
from datetime import date
import datetime
import tdsurface.depth.models


def mainmenu(request) :
    d = {}
    return render_to_response('mainmenu.html', d)