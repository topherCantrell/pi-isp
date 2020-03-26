
import RPi.GPIO as GPIO
import spidev  # https://github.com/doceme/py-spidev
import time

PIN_RESET = 5
WAIT_AFTER_RESET   = 0.5
WAIT_AFTER_ENABLE  = 0.5
WAIT_AFTER_ERASE   = 0.5
WAIT_AFTER_COMMAND = 0.001

class ISP8051:
    
    '''    
    From page 16 of https://www.keil.com/dd/docs/datashts/atmel/at89s52_ds.pdf
    
      - Pull the RST pin to Vcc
      - Send the Programming Enable instruction ()
      - Send a ChipErase before any programming
      - Send commands
      - Release RST (or drive low)
      - spi.close()
      - Frequency should be less than 1/16 of the crystal frequency:    
        8MHz crystal divided by 16 = 500,000
    
    https://www.corelis.com/education/tutorials/spi-tutorial/
    
    8051 clock active high (CPOL=0), data latched on leading low-to-high (CPHA=1)
    
    Commands (from 8051 datasheet):
    
    ProgEnable: 10101100_01010011_xxxxxxxx_xxxxxxxx
                                           01101001
    ChipErase : 10101100_100xxxxx_xxxxxxxx_xxxxxxxx
    ReadByte  : 00100000_xxxAAAAA_AAAAAAAA_xxxxxxxx
                                           DDDDDDDD
    WriteByte : 01000000_xxxAAAAA_AAAAAAAA_DDDDDDDD
    WriteLock : 10101100_111000ab_xxxxxxxx_xxxxxxxx
    ReadLock  : 00100100_xxxxxxxx_xxxxxxxx_xxcbaxx  ??
    ReadSig   : 00101000_xxxAAAAA                   ??
    ReadPage  : 00110000_xxxAAAAA_DDDDDDDD_DDDDDDDD ... 256 total D bytes
    WritePage : 01010000_xxxAAAAA_DDDDDDDD_DDDDDDDD ... 256 total D bytes
    
    '''
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_RESET,GPIO.IN)        
        self.spi = spidev.SpiDev()
        self.spi.open(0,0) # Device doesn't matter since we aren't using the CS line
        
        # Default settings
        #spi.bits_per_word = 8
        #spi.cshigh = False
        #spi.loop = False
        #spi.no_cs = False
        #spi.lsbfirst = False
        #spi.max_speed_hz = 125_000_000
        #spi.mode = 0 # CPOL/CPHA -> b00, b01, b10, b11
        #spi.threewire = False
        
        self.spi.lsbfirst = False
        self.spi.bits_per_word = 8
        self.spi.mode = 0
        self.spi.no_cs = True
        self.spi.max_speed_hz = 500000 # 250000 # 500000
        self.spi.threewire = False
        
        self.enable_programming()   
    
    def close(self):
        self.spi.close()
        self.set_reset(False)
            
    def set_reset(self,is_reset):
        if is_reset:      
            GPIO.setup(PIN_RESET,GPIO.OUT)      
            GPIO.output(PIN_RESET,GPIO.HIGH)            
        else:
            GPIO.setup(PIN_RESET,GPIO.IN)
            #GPIO.output(PIN_RESET,GPIO.LOW)
        time.sleep(WAIT_AFTER_RESET)
        
    def enable_programming(self):
        self.set_reset(True)
        a = self.spi.xfer2([0xAC,0x53,0x00,0x00])
        if a[3]!= 105:
            raise Exception('Expected a 0x69 ack')
        time.sleep(WAIT_AFTER_ENABLE)
    
    def erase(self):
        self.spi.xfer2([0xAC,0x80,0x00,0x00])
        time.sleep(WAIT_AFTER_ERASE)
        
    def is_blank(self):
        # TODO:all -- use pages
        for i in range(16): 
            if self.read_byte(i)!=255:
                return False
        return True
            
    def write_byte(self,addr,value):
        a1 = (addr>>8)&0x1F
        a2 = addr & 0xFF
        dat = [0x40,a1,a2,value]        
        self.spi.xfer2(dat)
        time.sleep(WAIT_AFTER_COMMAND)
    
    def read_byte(self,addr):
        a1 = (addr>>8)&0x1F
        a2 = addr & 0xFF
        dat = [0x20,a1,a2,0]    
        a = self.spi.xfer2(dat)
        time.sleep(WAIT_AFTER_COMMAND)
        return a[3]
        
    def write_bytes(self,addr,values):
        for v in values:
            self.write_byte(addr,v)
            addr += 1
    
    def read_bytes(self,addr,num):
        ret = []
        for _ in range(num):
            ret.append(self.read_byte(addr))
            addr += 1
        return ret
    
    def write_page(self,page_num,values):
        if len(values)!=256:
            raise Exception('Expected 256 values')
        a1 = page_num&0x1F
        raise Exception('Not Working')
        # Maybe try writing in bursts instead of one array of 256        
        dat = [0x50,a1]
        self.spi.xfer2(dat)
        time.sleep(WAIT_AFTER_COMMAND) 
        for i in range(32):
            self.spi.xfer2(values[i*8:(i+1)*8])
            time.sleep(0.5)
        time.sleep(WAIT_AFTER_COMMAND)        
    
    def read_page(self,page_num):
        a1 = page_num&0x1F
        dat = [0x30,a1] + ([0]*256)
        ret = self.spi.xfer2(dat)
        time.sleep(WAIT_AFTER_COMMAND)
        return ret[2:]

if __name__ == '__main__':
    
    isp = ISP8051()
    isp.set_reset(True)
    isp.enable_programming()
    isp.erase()
    