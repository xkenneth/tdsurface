
def hex2signedint(x, bits) :
    s = pow(2,bits-1)
    x = int(x,16)
    if x >= s :
        # Less than 0
        x = (pow(2,bits) - x) * -1
    return x


class ToolLogData :
    def __init__(self, raw_data) :
        self.raw_data = raw_data
        h = raw_data.split('\t')
        self.log_size = len(h) * 2
        i = [int(x, 16) for x in h]
        self.raw_data = raw_data
        self.seconds = int(h[0]+h[1],16)
        self.status = i[2]
        self.gravity_x = i[3]
        self.gravity_y = i[4]
        self.gravity_z = i[5]
        self.magnetic_x = i[6]
        self.magnetic_y = i[7]
        self.magnetic_z = i[8]
        self.temperature = i[9]
        self.gamma = []
        self.gamma = i[10:]            
        
        
class ToolSensorData :
    def __init__(self, raw_data) :
        self.raw_data = raw_data
        h = raw_data.split(' ')        
        i = [int(x, 16) for x in h]
        
        self.timer = int(h[0]+h[1],16)
        self.frame_id = i[2]
        self.status = i[3]
        self.inclination = i[4] * 180 / 10000.0
        self.azimuth = i[5] * 360 / 10000.0
        self.gravity = i[6] / 2000.0
        self.magnetic = i[7] / 2000.0
        self.gamma_ray = pow(10, i[8]*2/10000.0 ) * 2
        self.tool_face = i[9] * 360 /10000.0
        self.gravity_x = i[10]
        self.gravity_y = i[11]
        self.gravity_z = i[12]
        self.magnetic_x = i[13]
        self.magnetic_y = i[14]
        self.magnetic_z = i[15]
        self.temperature = i[16] * 500 / 10000.0
        self.pressure = i[17]

def signedint(x,bits) :
    s = pow(2,bits-1)    
    if x >= s :
        # Less than 0
        x = (pow(2,bits) - x) * -1
    return x

class StatusConstantProfile :
    def __init__(self, scp) :
        self.raw_data = scp
        self.advanced_sequence_pattern = bool(scp[3])
        self.tool_face_zeroing = bool(scp[4])
        self.rotation_sensing = bool(scp[5])
        self.logging_interval = (0x10000*scp[92]) + scp[93]
        self.motor_open_position_offset = signedint(scp[67],16)
        self.motor_shut_position_offset = signedint(scp[68],16)
        self.motor_open_max_acceleration = scp[79]
        self.motor_shut_max_acceleration = scp[80]
        self.motor_open_acceleration_delay = scp[73]
        self.motor_shut_acceleration_delay = scp[74]
        self.motor_calibration_initial_acceleration = scp[60]
        self.gammaray_log_size = scp[57]
        self.pulse_time = scp[8]
        self.code_pulse_time = scp[9]
        self.code_pulse_diff = scp[10]
        self.narrow_pulse_time = scp[11]
        self.wide_pulse_time = scp[12]
        self.gear_numerator = scp[18]
        self.gear_denominator = scp[19]

class MotorStatus :
    def __init__(self, s) :
        self.raw_data = s
        self.calibration_speed = int(s[0])
        self.open_position = hex2signedint(s[1],32)
        self.shut_position = hex2signedint(s[2],32)
