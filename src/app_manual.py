
import isp8051
ISP = isp8051.ISP8051()

ISP.erase()

data = ISP.read_bytes(0,20)
print(data)

ISP.write_bytes(0,[0x75,0xA0,0xAA,0x02,0x00,0x00])

data = ISP.read_bytes(0,20)
print(data)

ISP.close()
