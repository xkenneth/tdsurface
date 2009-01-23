
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
        self.gravity = i[6] / 10000.0
        self.magnetic = i[7] / 10000.0
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