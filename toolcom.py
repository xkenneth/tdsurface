import serial
import logging


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
        logging.info("out:0:%s" % s)
        self.ser.write(line)
        
    def read_line(self) :
        line = self.ser.readline()        
        logging.info("in:%d:%s" % (self.in_waiting(), line))
        return line
    
    def flush_input_buffer(self) :
        self.ser.flushInput()

    def in_waiting(self) :
        return self.ser.inWaiting()
            
    def close(self) :
        self.ser.close()