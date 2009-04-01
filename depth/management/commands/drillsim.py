from django.core.management.base import BaseCommand, CommandError
import os
import sys
import time
from datetime import datetime

from tdsurface.depth.models import ToolMWDRealTime
from tdsurface.depth.models import WITS0
from tdsurface.depth.models import Settings
from tdsurface.depth.models import Run

import random


class Command(BaseCommand):
    
    help = "Loads random MWD Realtime data every 5 seconds"        

    def handle(self, *args, **options):
        
        settings = Settings()
        active_run = settings.get_active_run()

        d=100
        h=d      
        for cnt in range(100) :
            m = 1
            if int(random.uniform(1,10)) == 1 :
                m = -1

            d += (int(random.uniform(1,10)) * m)

            if d - ((d/100)*100) <= 20 : 
                g = int(random.uniform(90,110))
            else :
                g = int(random.uniform(30,35))

            if d > h :
                h=d

            bd = WITS0(run=active_run, time_stamp=datetime.utcnow(), recid=1, itemid=8, value=d)
            bd.save()
            hd = WITS0(run=active_run, time_stamp=datetime.utcnow(), recid=1, itemid=10, value=h)
            hd.save()
            time.sleep(10)
            
            mdwrt = ToolMWDRealTime(run=active_run, time_stamp=datetime.utcnow(), type='gammaray', value=g )
            mdwrt.save()
            
            time.sleep(10)                        
                        
                        
                        
                        
                        
