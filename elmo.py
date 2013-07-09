import usb.core
import usb.util
from PIL import Image
import cStringIO as StringIO                                                    
import sys

class Elmo:
    device = None
    msg = {
        'version':   [0,0,0,0,0x18,0,0,0,0x10,0x8B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ,'picture':  [0,0,0,0,0x18,0,0,0,0x8e,0x80,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ,'buttons':  [0,0,0,0,24,0,0,0,0,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        ,'zoomin':   [0,0,0,0,0x18,0,0,0,0xE0,0,0,0,0x00,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #zoomin
        ,'zoomout':  [0,0,0,0,0x18,0,0,0,0xE0,0,0,0,0x01,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #zoomout
        ,'autofocus':[0,0,0,0,0x18,0,0,0,0xE1,0,0,0,0x00,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #autofocus?
        ,'brightness_dark': [0,0,0,0,0x18,0,0,0,0xE2,0,0,0,0x03,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ,'brightness_light': [0,0,0,0,0x18,0,0,0,0xE2,0,0,0,0x05,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    }
    last_image = None

    def connect(self,vendor=0x09a1,product=0x001d):
        self.device = usb.core.find(idVendor=vendor, idProduct=product)
        
        if self.device is None:
            return -1
        else:
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
                usb.util.claim_interface(self.device, 0)
        self.device.reset()                                                                  
        self.device.set_configuration()

        return self

    def zoom(self,i):
        if i > 0:
            self.device.write(self.device[0][(0,0)][1].bEndpointAddress,self.msg['zoomin'],0)
            ret = self.device.read(self.device[0][(0,0)][0].bEndpointAddress,32)
        elif i < 0:
            self.device.write(self.device[0][(0,0)][1].bEndpointAddress,self.msg['zoomout'],0)
            ret = self.device.read(self.device[0][(0,0)][0].bEndpointAddress,32)

    def focus(self,i):
        if i == 0: 
            self.autofocus()

    def brightness(self,i):
        try:
            if i > i:
                self.device.write(self.device[0][(0,0)][1].bEndpointAddress,self.msg['brightness_dark'],0)
                ret = self.device.read(self.device[0][(0,0)][0].bEndpointAddress,32)
                return ret
            elif i < i:
                self.device.write(self.device[0][(0,0)][1].bEndpointAddress,self.msg['brightness_light'],0)
                ret = self.device.read(self.device[0][(0,0)][0].bEndpointAddress,32)
                return ret 
        except:
            return False

    
    def autofocus(self):
        try:
            self.device.write(self.device[0][(0,0)][1].bEndpointAddress,self.msg['autofocus'],0) 
            ret = self.device.read(self.device[0][(0,0)][0].bEndpointAddress,32)
            return ret
        except:
            return False

    def version(self):
        try:
            self.device.write(self.device[0][(0,0)][1].bEndpointAddress,self.msg['version'],0)
            ret = self.device.read(self.device[0][(0,0)][0].bEndpointAddress,32)
            return ret
        except:
            return False
    
    def cleardevice(self):
        '''Clear the devices memory'''
        while True:
            try:
                results = self.device.read(0x83, 512)
            except usb.core.USBError as e:
                if e.args[0] == 'Operation timed out' :
                    break # timeout and swiped means we are done

    def get_image(self):
        # Try to read a picture until you get a valid stream
        try:
            self.device.write(0x04, self.msg['picture'],0)
            tmp = self.device.read(0x83,32)
        except:
            self.cleardevice()
            return self.last_image

        # Every package has a defined length in byte 4/5 of the first 8 Bytes
        # which is used to read the whole package
        finished = False                                                            
        error = False
        answer = []
        size = 0xfef8
        
        # 0xfef8 is the maximum size of a package
        # if it is smaller => the last package and exit
        while size == 0xfef8:                                                         
            try:
                ret = self.device.read(0x83,512)                                               
                size = 256*ret[5]+ret[4]#-(512-8) # Byte to integer 
                answer += ret[8:]
                answer += self.device.read(0x83,size)                                        
            except:
                self.cleardevice()
                error = True
                return self.last_image
                break                                                     

        if not error:
            data = ''.join([chr(i) for i in answer])
            try:
                stream = StringIO.StringIO(data)
                image = Image.open(stream)
                self.last_image = image
            except:
                self.cleardevice()
            return self.last_image
