import time
import datetime
import toolsensor
from tooldata import ToolLogData
from tooldata import ToolSensorData

class ToolAPI :
    def __init__(self, toolcom) :
        self.toolcom = toolcom

    
    # Convert Tool Time to python datetime
    def _tooltime2datetime(cls,s) :
        l = s.split(' ')
        
        y = 2000 + int(l[0],16)
        m = int(l[1],16)
        d = int(l[2],16)
        
        h = int(l[3],16)
        n = int(l[4],16)
        s = int(l[5],16)        
    
        return datetime.datetime(y,m,d,h,m,s)
    
    # Convert tool time to seconds
    def _tooltime2timer(cls,s) :
        l = s.split(' ')
        
        #y = int(l[0],16)   # ignore years
        #m = int(l[1],16)   # ignore months
        d = int(l[2],16)
        
        h = int(l[3],16)
        n = int(l[4],16)
        s = int(l[5],16)        
    
        return s + (60 * n) + (3600 * h) + (86400 * (d-1)) 
    
    # Convert tool log times to python datetime   
    def tool_seconds2datetime(high,low) :
        seconds = int(high+low,16)
        
    
    def get_timer(self) :
        self.raw_data = []
        self.toolcom.write_line('T')
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        s = self.decruft(raw)

        return self._tooltime2timer(s)
        
   
    def get_time(self) :
        self.raw_data = []
        self.toolcom.write_line('T')
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        s = self.decruft(raw)

        return self._tooltime2datetime(s)
    

    def set_time(self,dt) :
        self.raw_data = []
        
        #Set seconds first so that the time will be more accurate
        self.toolcom.write_line('TS ' + hex(dt.second)[2:])     # Remove the '0x' from the beginning of hex strings
        self.raw_data.append(self.toolcom.read_line())          # Each set commands returns a tooltime string.  Only return the last one
        
        self.toolcom.write_line('TN ' + hex(dt.minute)[2:])
        self.raw_data.append(self.toolcom.read_line())
        
        self.toolcom.write_line('TH ' + hex(dt.hour)[2:])
        self.raw_data.append(self.toolcom.read_line())
        
        self.toolcom.write_line('TD ' + hex(dt.day)[2:])
        self.raw_data.append(self.toolcom.read_line())
        
        self.toolcom.write_line('TM ' + hex(dt.month)[2:])
        self.raw_data.append(self.toolcom.read_line())
        
        self.toolcom.write_line('TY ' + hex(dt.year-2000)[2:])  # Send years since 2000
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        
        s = self.decruft(raw)
        return self._tooltime2datetime(s)
    
    def echo(self, s) :
        self.raw_data=[]
        self.toolcom.write_line('E ' + s)
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        return self.decruft(raw)
    
    def decruft(self, s) :
        s = s.strip(' >\n\r\0\t')  # Strip the line endings and beginning of line '>>'
        s = s.replace('\0', '')  # Remove null characters sent between each char in older firmwares      
        return(s)
        
    def get_calibration_contants(self) :
        self.raw_data = []
        self.toolcom.write_line('RC')
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        s = self.decruft(raw)
        return s.split(' ')
        
    def get_log(self, call_back) :
        self.raw_data = []
        self.toolcom.write_line('RL')
        
        bad_data_cnt = 0   #Safty valve in case the tool wigs out
        f_cnt = 0
        while True :
            if f_cnt > 2 :
                break
            
            raw = self.toolcom.read_line()
            s = self.decruft(raw)
            l = s.split('\t')
            if not len(l) :                         # Check for data
                bad_data_cnt += 1
                continue
            else :
                bad_data_cnt = 0                    
            
            if l[0] == 'FFFF' :                     # Check for possible end of data
                f_cnt+=1
                if f_cnt >= 2 :                     # End of Data if at least two line contain FFFF in the time
                    break
                continue
            
            f_cnt = 0            
            if not call_back( ToolLogData(s) ) :   # If call back returns false, cancel the download
                break
            
            if bad_data_cnt > 10 :
                break;
        
        self.toolcom.write('\x1b')
        time.sleep(2)
        self.toolcom.flush_input_buffer()
        

    def get_sensor_readings(self) :
        self.raw_data = []
        self.toolcom.write_line('S')
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        s = self.decruft(raw)        
        sensor = ToolSensorData(s)
        return sensor

    def purge_log(self) :
        self.raw_data = []
        self.toolcom.write_line('WE')
        for x in range(10) :
            if self.toolcom.in_waiting() :
                break
            time.sleep(10)
            
        self.raw_data.append(self.toolcom.read_line())  # Read '>> Flash erased!\r\n'
        self.raw_data.append(self.toolcom.read_line())  # Read the log start address '>> D600\r\n'        

    def get_current_log_address(self) :
        self.raw_data = []
        self.toolcom.write_line('RS')
        raw = self.toolcom.read_line()
        self.raw_data.append(raw)
        return self.decruft(raw)
        
    
        
        