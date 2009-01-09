from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys
import time
from datetime import datetime

from xml.etree import ElementTree as ET
import glob

from tdsurface.depth.models import MWDRealTime
from tdsurface.depth.models import Settings
from tdsurface.depth.models import Run




class Command(BaseCommand):
    
    help = "Loads an MWD Log into the MWDRealTime table"
    args = 'log_file_name ...'

    value_types = {'azimuth':'A', 'gammaray':'R', 'inclination':'I'}

    def handle(self, *args, **options):
        
        settings = Settings()
        active_run = settings.get_active_run()
        
        for wildCard in args :
            fileNames = glob.glob(wildCard)
            for inFileName in fileNames :
                inFile = open(inFileName)
                for line in inFile :
                    e = ET.XML(line)
                    type = e.getiterator('type')[0].text
                    value = e.getiterator('value')[0].text
                    sts = e.getiterator('timestamp')[0].text                    
                    try :
                        timestamp = datetime.strptime(sts[:8]+sts[12:],'%I:%M:%S %p %m/%d/%Y')
                        microsecond = int(sts[9:12]) * 1000
                        timestamp.replace(microsecond=microsecond)
                    except ValueError:
                        try :
                            timestamp = datetime.strptime(sts, '%I:%M:%S.%p %m/%d/%Y')
                        except ValueError:                                
                                timestamp = datetime.strptime(sts[:7]+sts[11:],'%I:%M:%S %p %m/%d/%Y')
                                microsecond = int(sts[8:11]) * 1000
                                timestamp.replace(microsecond=microsecond)
                                
                    if type not in self.value_types.keys() :
                        print 'unknown type:', type
                        continue
                        
                    mdwrt = MWDRealTime(run=active_run, time_stamp=timestamp, type=self.value_types[type], value=int(float(value)) )
                    mdwrt.save()
                        
                        
                        
                        
                        
                        