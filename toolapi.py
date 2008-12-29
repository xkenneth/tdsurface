import time
import datetime

class ToolAPI :
    def __init__(self, toolcom) :
        self.toolcom = toolcom


    def _tooltime2datetime(cls,s) :
        l = s.split(' ')
        
        y = 2000 + int(l[0],16)
        m = int(l[1],16)
        d = int(l[2],16)
        
        h = int(l[3],16)
        n = int(l[4],16)
        s = int(l[5],16)        
    
        return datetime.datetime(y,m,d,h,m,s)
    
   
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
        
    def get_log(self, call_back=None) :
        self.raw_data = []
        self.toolcom.write_line('RL')
        log = []
        while True :
            raw = self.toolcom.read_line()
            self.raw_data.append(raw)
            s = self.decruft(raw)
            l = s.split('\t')
            log.append(l)
            if call_back :
                call_back(l)
            if 'FFFF' in l :
                break
        
        self.toolcom.write('\x1b')
        time.sleep(2)
        self.toolcom.flush_input_buffer()
        
        return log

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
        
    
        
        