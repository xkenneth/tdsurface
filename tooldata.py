
class ToolLogData :
    def __init__(self, raw_data) :
        self.raw_data = raw_data
        h = raw_data.split('\t')
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
        self.gamma0 = i[10]
        self.gamma1 = i[11]
        self.gamma2 = i[12]
        self.gamma3 = i[13]
        
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
        self.gravity = i[6] / 1000.0
        self.magnetic = i[7] / 1000.0
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
        self.advanced_squence_pattern = bool(scp[3])
        self.tool_face_zeroing = bool(scp[4])
        self.rotation_sensing = bool(scp[5])
        self.logging_interval = (0x10000*scp[88]) + scp[89]
        self.motor_open_position_offset = signedint(scp[65],16)
        self.motor_shut_position_offset = signedint(scp[66],16)
        self.motor_open_max_acceleration = scp[75]
        self.motor_shut_max_acceleration = scp[76]
        self.motor_open_acceleration_delay = scp[69]
        self.motor_shut_acceleration_delay = scp[70]
        self.motor_calibration_initial_acceleration = scp[60]

class MotorStatus :
    def __init__(self, s) :
        self.raw_data = s
        self.calibration_speed = s[0]
        self.open_position = s[1]
        self.shut_position = s[2]
