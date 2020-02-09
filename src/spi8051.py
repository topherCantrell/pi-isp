
import RPi.GPIO as GPIO
import spidev  # https://github.com/doceme/py-spidev
import time

# Could always bit-bang the signals

PIN_RESET = 5

class ISP8051:
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_RESET,GPIO.OUT)
        self.set_reset(False)
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
        self.spi.max_speed_hz = 250000 # 500000
        self.spi.threewire = False
        
    def set_reset(self,is_reset):
        if is_reset:
            GPIO.output(PIN_RESET,GPIO.HIGH)
        else:
            GPIO.output(PIN_RESET,GPIO.LOW)

#to_send = [0x01, 0x02, 0x03]
#a = spi.xfer2(to_send)

# We want to hold the reset high through the whole session. Release it to
# allow the processor to boot

# From page 16 of https://www.keil.com/dd/docs/datashts/atmel/at89s52_ds.pdf

# - Pull the RST pin to Vcc
# - Send the Programming Enable instruction ()
# - Send a ChipErase before any programming
# - Frequency should be less than 1/16 of the crystal frequency
# - Release RST (or drive low)

# - 8MHz crystal divided by 16 = 500,000

# https://www.corelis.com/education/tutorials/spi-tutorial/

# 8051 clock active high (CPOL=0), data latched on leading low-to-high (CPHA=1)

#spi.close()

# erase()
#
# read_byte(addr) -> int
# read_page(page_addr) -> list
# read_lock_bits() -> list
#
# write_byte(addr,value)
# write_page(addr,list)
# write_lock_bits(list)


# ProgEnable: 10101100_01010011_xxxxxxxx_xxxxxxxx
#                                        01101001
# ChipErase : 10101100_100xxxxx_xxxxxxxx_xxxxxxxx
# ReadByte  : 00100000_xxxAAAAA_AAAAAAAA_xxxxxxxx
#                                        DDDDDDDD
# WriteByte : 01000000_xxxAAAAA_AAAAAAAA_DDDDDDDD
# WriteLock : 10101100_111000ab_xxxxxxxx_xxxxxxxx
# ReadLock  : 00100100_xxxxxxxx_xxxxxxxx_xxcbaxx  ??
# ReadSig   : 00101000_xxxAAAAA                   ??
# ReadPage  : 00110000_xxxAAAAA_DDDDDDDD_DDDDDDDD ... 256 total D bytes
# WritePage : 01010000_xxxAAAAA_DDDDDDDD_DDDDDDDD ... 256 total D bytes


# Manual test before I make methods ...

isp = ISP8051()

isp.set_reset(True) # Hold the reset line active
time.sleep(1)

# Enable program mode
a = isp.spi.xfer2([0xAC,0x53,0x00,0x00])
print('Enable program mode',a)

time.sleep(1) # Lots of sleeps here just for testing

# Erase the chip
a = isp.spi.xfer2([0xAC,0x80,0x00,0x00])
print('Erase chip',a)

time.sleep(1)

# Simple program that relays P2 (input pins) to P1 (LEDs)
# Use jumper wires between inputs and ground/5V to test
prg = [0x75,0xA0,0xFF,  # MOV P2,$FF
       0x85,0xA0,0x90,  # MOV P1,P2
       0x02,0x00,0x00]  # LJMP $0000

addr = 0
for p in prg:
    a1 = (addr>>8)&0xFF
    a2 = addr & 0xFF
    dat = [0x40,a1,a2,p]
    print('Sending',dat)
    isp.spi.xfer2(dat)
    addr += 1
    time.sleep(.1)
    
time.sleep(1)

for addr in range(12):
    a1 = (addr>>8)&0xFF
    a2 = addr & 0xFF
    dat = [0x20,a1,a2,0]    
    a = isp.spi.xfer2(dat)
    print('Read address',addr,'=',a[3])
    addr += 1
    time.sleep(.1)

# Let the processor run
isp.set_reset(False)