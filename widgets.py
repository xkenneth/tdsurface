# widgets.py
#
# To use you have to put calendar/ (from http://www.dynarch.com/projects/calendar/)
# to your MEDIA folder and then include such links on your page:
# <!-- calendar -->
# <link rel="stylesheet" type="text/css" href="{{ MEDIA_URL }}calendar/calendar-win2k-cold-2.css" />
#<script type="text/javascript" src="{{ MEDIA_URL }}calendar/calendar.js"></script>
# <!-- this is translation file - choose your language here -->
#<script type="text/javascript" src="{{ MEDIA_URL }}calendar/lang/calendar-pl.js"></script>
#<script type="text/javascript" src="{{ MEDIA_URL }}calendar/calendar-setup.js"></script>
#<!-- /calendar -->

from django.utils.encoding import force_unicode
from django.conf import settings
from django import forms
#from datetime import datetime, time
import time
import datetime


# DynarchDateTime Widget
datetime_button_html = u"""<img src="%s/calendar/timebutton.png" alt="calendar" id="%s_btn" style="display: inline; vertical-align: text-bottom; cursor: pointer; border: 0px solid #8888aa;" title="Select date and time"
            onmouseover="this.style.background='#444444';" onmouseout="this.style.background=''" />
<script type="text/javascript">
    Calendar.setup({
        inputField     :    "%s",
        ifFormat       :    "%s",
        button         :    "%s_btn",
        singleClick    :    true,
        showsTime      :    true
    });
</script>"""

date_button_html = u"""<img src="%s/calendar/datebutton.png" alt="calendar" id="%s_btn" style="display: inline; vertical-align: text-bottom; cursor: pointer; border: 0px solid #8888aa;" title="Select date and time"
            onmouseover="this.style.background='#444444';" onmouseout="this.style.background=''" />
<script type="text/javascript">
    Calendar.setup({
        inputField     :    "%s",
        ifFormat       :    "%s",
        button         :    "%s_btn",
        singleClick    :    true,
        showsTime      :    false
    });
</script>"""

class DynarchDateTimeWidget(forms.widgets.TextInput):
    
    def __init__(self, button_html, format = '%Y-%m-%d %H:%M:%S') :
        forms.widgets.TextInput.__init__(self)
        self.button_html = button_html
        self.dformat = format
    
    class Media:
        css = {            
            'all': ('/tdsurface/media/calendar/calendar-blue2.css', )    
        }
        js = ('/tdsurface/media/calendar/calendar.js',
              '/tdsurface/media/calendar/lang/calendar-en.js',
              '/tdsurface/media/calendar/calendar-setup.js',
              )
    
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': 
            try:
                final_attrs['value'] = \
                                   force_unicode(value.strftime(self.dformat))
            except:
                final_attrs['value'] = \
                                   force_unicode(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        id = final_attrs['id']
        
        jsdformat = self.dformat #.replace('%', '%%')
        cal = self.button_html % (settings.MEDIA_URL, id, id, jsdformat, id)
        a = u'<input%s /> %s' % (forms.util.flatatt(final_attrs), cal)
        return a

    def value_from_datadict(self, data, files, name):
        dtf = forms.fields.DEFAULT_DATETIME_INPUT_FORMATS
        empty_values = forms.fields.EMPTY_VALUES

        value = data.get(name, None)
        if value in empty_values:
            return None
        if isinstance(value, datetime.datetime):        
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
            
        for format in dtf:
            try:
                return datetime.datetime(*time.strptime(value, format)[:6])                
            except ValueError:
                continue
        return None
