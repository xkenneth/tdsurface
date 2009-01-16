import serial

DEBUG = True

if DEBUG :
    import logging
    LOG_FILENAME = '/tmp/toolcom.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)


class ToolCom :
    def __init__(self, **args) :
        self.raw_data = []
        self.ser = None
        self.ser = serial.Serial(**args)
        self.ser.flushInput()        
        
    
    def write(self, s) :
        self.ser.write(s)
        
    def write_line(self, s) :
        line = s + '\r'
        if DEBUG :
            logging.debug("out '%s'" % s)
        self.ser.write(line)
        
    def read_line(self) :
        line = self.ser.readline()
        if DEBUG :
            logging.debug("in '%s'" % line)
        return line
    
    def flush_input_buffer(self) :
        self.ser.flushInput()

    def in_waiting(self) :
        return self.ser.inWaiting()
            
    def close(self) :
        self.ser.close()