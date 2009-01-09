from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys
import time
from datetime import datetime

from xml.etree import ElementTree as ET
import glob

from tdsurface.depth.models import WITS0
from tdsurface.depth.models import Settings
from tdsurface.depth.models import Run

class Command(BaseCommand):
    
    help = "Loads a WITS0 Log into the WITS0 table tagged with the Active Run"
    args = 'log_file_name ...'

    def handle(self, *args, **options):
        
        settings = Settings()
        active_run = settings.get_active_run()
        
        for wildCard in args :
            fileNames = glob.glob(wildCard)
            for inFileName in fileNames :
                inFile = open(inFileName)
                for line in inFile :
                    e = ET.XML(line)
                    sts = e.getiterator('timestamp')[0].text                    
                    witsdatas = e.getiterator('witsdata')
                    for data in witsdatas :
                        id = data.getiterator('identifier')[0].text
                        value = data.getiterator('value')[0].text
                    
                        wits0 = WITS0(run=active_run, time_stamp=sts, recid=id[:2], itemid=id[2:], value=value )
                        wits0.save()
                        
                        
                        
                        
                        
                        