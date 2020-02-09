import unittest

import isp8051

class Test_8051(unittest.TestCase):
    
    def setUp(self):
        self.isp = isp8051.ISP8051()
        self.isp.set_reset(True)   
        self.isp.enable_programming()    
        self.isp.erase()
    
    def tearDown(self):
        self.isp.close()

    def test_enable(self):        
        pass        
        
    def test_erase_chip(self):
        self.isp.write_byte(8,0xA5)
        self.assertTrue(not self.isp.is_blank())
        self.isp.erase()
        self.assertTrue(self.isp.is_blank())
        
    def test_is_blank(self):
        self.assertTrue(self.isp.is_blank())
        self.isp.write_byte(8,0xA5)
        self.assertTrue(not self.isp.is_blank())
        self.isp.erase()
        self.assertTrue(self.isp.is_blank())
        
    def test_write_byte(self):
        self.isp.write_byte(0,0x00)
        self.assertTrue(self.isp.read_byte(0)==0x00)
        self.isp.write_byte(1024,0x10)
        self.assertTrue(self.isp.read_byte(1024)==0x10)
        self.isp.write_byte(2048,0x20)
        self.assertTrue(self.isp.read_byte(2048)==0x20)
        self.isp.write_byte(4096,0x30)
        self.assertTrue(self.isp.read_byte(4096)==0x30)
        self.isp.write_byte(8191,0x30)
        self.assertTrue(self.isp.read_byte(8191)==0x30)
        
    def test_write_bytes(self):
        self.isp.write_bytes(0,[1,2,3,4])
        self.assertTrue(self.isp.read_byte(0)==1)
        self.assertTrue(self.isp.read_byte(1)==2)
        self.assertTrue(self.isp.read_byte(2)==3)
        self.assertTrue(self.isp.read_byte(3)==4)
        
    def test_write_256_bytes(self):
        dat = []
        for i in range(256):
            dat.append(i)
        self.isp.write_bytes(0,dat)
        a = self.isp.read_bytes(0,256)
        self.assertTrue(a==dat)
        
    def test_read_bytes(self):
        self.isp.write_byte(0,10)
        self.isp.write_byte(1,20)
        self.isp.write_byte(2,30)
        self.isp.write_byte(3,40)
        a = self.isp.read_bytes(0,4)        
        self.assertTrue(a==[10,20,30,40])
        
    def test_read_page(self):
        dat = []
        for i in range(256):
            dat.append(i)
        self.isp.write_bytes(20*256,dat)
        
        a = self.isp.read_page(20)
        self.assertTrue(a==dat)
        
        
    def ftest_write_page(self):
        exp = []
        for i in range(256):
            exp.append(i)
        self.isp.write_page(1,exp)
        
        a = self.isp.read_bytes(256,256)
        print(a)
        
        
        