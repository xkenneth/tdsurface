import time
import datetime

from tooldata import ToolLogData
from tooldata import ToolSensorData
from tooldata import StatusConstantProfile
from tooldata import MotorStatus

calibration_map = {
    'accelerometer_x_offset': 0,
    'accelerometer_x_gain': 1,
    'accelerometer_y_offset': 2,
    'accelerometer_y_gain': 3,
    'accelerometer_z_offset': 4,
    'accelerometer_z_gain': 5,
    'magnetometer_x_offset': 6,
    'magnetometer_x_gain': 7,
    'magnetometer_y_offset': 8,
    'magnetometer_y_gain': 9,
    'magnetometer_z_offset': 10,
    'magnetometer_z_gain': 11,
    'temperature_offset': 12,
    'temperature_gain': 13
}


def hex2signedint(x, bits) :
    s = pow(2,bits-1)
    x = int(x,16)
    if x >= s :
        # Less than 0
        x = (pow(2,bits) - x) * -1
    return x
        


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
        self.toolcom.write_line('T')
        raw = self.toolcom.read_line()        
        s = self.decruft(raw)

        return self._tooltime2timer(s)
        
   
    def get_time(self) :        
        self.toolcom.write_line('T')
        raw = self.toolcom.read_line()        
        s = self.decruft(raw)

        return self._tooltime2datetime(s)
    

    def set_time(self,dt) :        
        
        #Set seconds first so that the time will be more accurate
        self.toolcom.write_line('TS ' + hex(dt.second)[2:])     # Remove the '0x' from the beginning of hex strings
        self.toolcom.read_line()          # Each set commands returns a tooltime string.  Only return the last one
        
        self.toolcom.write_line('TN ' + hex(dt.minute)[2:])
        self.toolcom.read_line()
        
        self.toolcom.write_line('TH ' + hex(dt.hour)[2:])
        self.toolcom.read_line()
        
        self.toolcom.write_line('TD ' + hex(dt.day)[2:])
        self.toolcom.read_line()
        
        self.toolcom.write_line('TM ' + hex(dt.month)[2:])
        self.toolcom.read_line()
        
        self.toolcom.write_line('TY ' + hex(dt.year-2000)[2:])  # Send years since 2000
        raw = self.toolcom.read_line()        
        
        s = self.decruft(raw)
        return self._tooltime2datetime(s)
    
    def echo(self, s) :        
        self.toolcom.write_line('E ' + s)
        return self.decruft(self.toolcom.read_line())        
    
    def decruft(self, s) :
        s = s.strip(' >\n\r\0\t')  # Strip the line endings and beginning of line '>>'
        s = s.replace('\0', '')  # Remove null characters sent between each char in older firmwares      
        return(s)
        
    def get_calibration_contants(self) :        
        self.toolcom.write_line('RC')
        return [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        
    def set_calibration_contant(self, coeff, val) :
        if type(coeff) != type(1) :
            coeff = calibration_map[coeff]
        cmd = ' '.join(('WC', hex(coeff)[2:], hex(val)[2:]))
        self.toolcom.write_line(cmd)
        return [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]        
        
    def get_log(self, call_back) :        
        self.toolcom.write_line('RL')
        
        bad_data_cnt = 0   #Safty valve in case the tool wigs out
        f_cnt = 0
        canceled = False
        error = False
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
                canceled=True
                break
            
            if bad_data_cnt > 10 :
                error = True
                break;
        
        self.toolcom.write('\x1b')
        time.sleep(2)
        self.toolcom.flush_input_buffer()
        if error :
            return None
        if canceled :
            return False
        return True
        

    def get_sensor_readings(self) :        
        self.toolcom.write_line('S')
        raw = self.toolcom.read_line()        
        s = self.decruft(raw)        
        sensor = ToolSensorData(s)
        return sensor

    def purge_log(self) :        
        self.toolcom.write_line('WE')
        for x in range(10) :
            if self.toolcom.in_waiting() :
                break
            time.sleep(10)
            
        self.toolcom.read_line()  # Read '>> Flash erased!\r\n'
        self.toolcom.read_line()  # Read the log start address '>> D600\r\n'        

    def get_current_log_address(self) :        
        self.toolcom.write_line('RS')
        raw = self.toolcom.read_line()        
        return self.decruft(raw)

    def get_bytes_in_log(self) :    
        log_address = self.get_current_log_address()
        bytes_in_log = int(log_address, 16) - int('E600', 16)
        return bytes_in_log
        
    def _getset_pulse_pattern_profile(self, cmd) :
        self.toolcom.write_line(cmd)
        ppp = []
        for x in range(3) :            
            p = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]                    
            c = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
            l = []
            for x in range(len(p)) :
                l.append((p[x],c[x]))
            ppp.append(l)
            
        return ppp
    
    def get_pulse_pattern_profile(self) :
        return self._getset_pulse_pattern_profile('RP')
        
    def set_pulse_pattern_profile(self, seq, num, pat, cnt) :    
        cmd = ' '.join(('WP',str(seq), hex(num)[2:], hex(pat)[2:], hex(cnt)[2:]))
        return self._getset_pulse_pattern_profile(cmd)
    
    def _getset_pulse_pattern_sequence_profile(self,cmd) :
        self.toolcom.write_line(cmd)
        ppsp = []
        
        s = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        hl = self.decruft(self.toolcom.read_line()).split(' ')
        t = [ int(hl[l]+hl[l+1], 16) for l in range(0,20,2) ]
            
        for x in range(len(s) ) :
            ppsp.append((s[x],t[x]))        
            
        return ppsp    
    
    def get_pulse_pattern_sequence_profile(self) :
        return self._getset_pulse_pattern_sequence_profile('RQ')
        
    def set_pulse_pattern_sequence_profile(self, num, seq, time) :
        cmd = ' '.join(('WQ',str(num), hex(seq)[2:], hex(time)[2:]))
        return self._getset_pulse_pattern_sequence_profile(cmd)

    def _get_status_constant_profile(self,cmd) :
        self.toolcom.write_line(cmd)        
        scp = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        scp += [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        scp += [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        self.toolcom.read_line()
        return StatusConstantProfile(scp)        

    def _set_status_constant_profile(self,cmd) :
        self.toolcom.write_line(cmd)        
        scp = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        scp += [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        scp += [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        self.toolcom.read_line()
        self.toolcom.read_line()
        return StatusConstantProfile(scp)      
        
    def get_status_constant_profile(self) :
        return self._get_status_constant_profile('RT')
    
    def toggle_advanced_sequence_pattern_mode(self) :
        return self._get_status_constant_profile('MY')

    def toggle_tool_face_zeroing(self) :
        return self._get_status_constant_profile('STR')

    def toggle_rotation_sensing(self) :
        return self._get_status_constant_profile('ORR')

    def set_logging_interval(self, time) :
        cmd = ' '.join(('TR', hex(time)[2:]))
        return self._get_status_constant_profile(cmd)

    def _set_motor_position_offset(self, cmd, v) :
        if v < 0 :
            v = 0xFFFF + (v + 1)
        cmd = ' '.join( (cmd, hex(v)[2:]) )
        return self._set_status_constant_profile(cmd)

    def set_motor_open_position_offset(self, v) :
        return self._set_motor_position_offset('MOF',v)

    def set_motor_shut_position_offset(self, v) :
        return self._set_motor_position_offset('MSF',v)

    def set_motor_open_max_acceleration(self, v) :
        cmd = ' '.join(('MWUOM', hex(v)[2:]) )
        return self._get_status_constant_profile(cmd)

    def set_motor_shut_max_acceleration(self, v) :
        cmd = ' '.join(('MWUSM', hex(v)[2:]) )
        return self._get_status_constant_profile(cmd)

    def set_motor_open_acceleration_delay(self, v) :
        cmd = ' '.join(('MWUO', hex(v)[2:]) )
        return self._get_status_constant_profile(cmd)

    def set_motor_shut_acceleration_delay(self, v) :
        cmd = ' '.join(('MWUS', hex(v)[2:]) )
        return self._get_status_constant_profile(cmd)

    def set_motor_calibration_initial_acceleration(self, v) :
        cmd = ' '.join(('MLP', hex(v)[2:]) )
        return self._get_status_constant_profile(cmd)

    def get_motor_status(self) :        
        self.toolcom.write_line('MLT')
        s = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        
        return MotorStatus(s)

    def motor_capture(self) :
        self.toolcom.write_line('MC')

    def motor_release(self) :
        self.toolcom.write_line('MR')

    def motor_open(self) :
        self.toolcom.write_line('MO')

    def motor_shut(self) :
        self.toolcom.write_line('MS')

    def motor_calibrate(self) :
        self.toolcom.write_line('MC')
        time.sleep(2)
        self.toolcom.write_line('ML')

        for x in range(10) :
            self.toolcom.read_line()    # Ignore calibration data

        s = [ int(x, 16) for x in self.decruft(self.toolcom.read_line()).split(' ') ]
        
        return MotorStatus(s)
