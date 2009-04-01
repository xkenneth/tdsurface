from django.core.management.base import BaseCommand, CommandError
import os
import sys
import time
from datetime import datetime

from tdsurface.depth.models import ToolMWDRealTime
from tdsurface.depth.models import Settings
from tdsurface.depth.models import Run

import random


class Command(BaseCommand):
    
    help = "Loads random MWD Realtime data every 5 seconds"        

    def handle(self, *args, **options):
        
        settings = Settings()
        active_run = settings.get_active_run()

        g = 30
        m = 1
        for cnt in range(100) :
            g += (int(random.uniform(1,15)) * m)
            print g
            mdwrt = ToolMWDRealTime(run=active_run, time_stamp=datetime.utcnow(), type='gammaray', value=g )
            mdwrt.save()
            if g>75 :
                m=-1
            if g<30 :
                m=1
            time.sleep(20)                        
                        
                        
                        
                        
                        
