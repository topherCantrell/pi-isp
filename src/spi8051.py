
import RPi.GPIO as GPIO
import spidev  # https://github.com/doceme/py-spidev

# Could always bit-bang the signals


GPIO.setmode(GPIO.BCM)

# GPIO5 = reset
GPIO.setup(5,GPIO.OUT)

GPIO.output(5,GPIO.HIGH) # To reset
GPIO.output(5,GPIO.LOW) # To run

spi = spidev.SpiDev()
spi.open(0, 1) # Not using the driver-controlled chip-select

# Default settings
#spi.bits_per_word = 8
#spi.cshigh = False
#spi.loop = False
#spi.no_cs = False
#spi.lsbfirst = False
#spi.max_speed_hz = 125_000_000
#spi.mode = 0 # CPOL/CPHA -> b00, b01, b10, b11
#spi.threewire = False

spi.lsbfirst = False
spi.bits_per_word = 8
spi.mode = 0
spi.no_cs = True
spi.max_speed_hz = 250000 # 500000
spi.threewire = False

to_send = [0x01, 0x02, 0x03]
a = spi.xfer2(to_send)

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



spi.close()

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
