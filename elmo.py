import usb.core
import usb.util

class Elmo:
    def __init__(self):
        self.device = None
        self.msg = {
            'version':   [0,0,0,0,0x18,0,0,0,0x10,0x8B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'picture':  [0,0,0,0,0x18,0,0,0,0x8e,0x80,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'buttons':  [0,0,0,0,24,0,0,0,0,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

            ,'zoom_stop':   [0,0,0,0,0x18,0,0,0,0xE0,0,0,0,0x00,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] 
            ,'zoom_in':  [0,0,0,0,0x18,0,0,0,0xE0,0,0,0,0x01,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] 
            ,'zoom_out': [0,0,0,0,0x18,0,0,0,0xE0,0,0,0,0x02,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'focus_auto':[0,0,0,0,0x18,0,0,0,0xE1,0,0,0,0x00,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'brightness_stop': [0,0,0,0,0x18,0,0,0,0xE2,0,0,0,0x04,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'brightness_dark': [0,0,0,0,0x18,0,0,0,0xE2,0,0,0,0x03,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'brightness_light': [0,0,0,0,0x18,0,0,0,0xE2,0,0,0,0x02,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'brightness_auto': [0,0,0,0,0x18,0,0,0,0xE2,0,0,0,0x05,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'focus_wide':  [0,0,0,0,0x18,0,0,0,0xEA,0,0,0,0x00,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] 
            ,'focus_near':  [0,0,0,0,0x18,0,0,0,0xEA,0,0,0,0x01,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            ,'focus_stop':  [0,0,0,0,0x18,0,0,0,0xEA,0,0,0,0x02,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        }
        self.zooming = False
        self.brightnessing = False
        self.focusing = False

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
        if self.zooming:
            self.device.write(0x02,self.msg['zoom_stop'],0)
            ret = self.device.read(0x81,32)
            self.zooming = False
            return

        if i > 0:   self.device.write(0x02,self.msg['zoom_in'],0)
        elif i < 0: self.device.write(0x02,self.msg['zoom_out'],0)
        self.zooming = True
        ret = self.device.read(0x81,32)

    def focus(self,i):
        if self.focusing:                                                        
            self.device.write(0x02,self.msg['focus_stop'],0)
            ret = self.device.read(0x81,32)
            self.focusing = False                                                
            return                                                              
                                                                                
        if i > 0:   self.device.write(0x02,self.msg['focus_wide'],0)
        elif i < 0: self.device.write(0x81,self.msg['focus_near'],0)
        else:
            self.autofocus()
            return
        self.focusing = True
        ret = self.device.read(0x81,32)
        


    def brightness(self,i):
        if self.brightnessing:                                                        
            self.device.write(0x02,self.msg['brightness_stop'],0)
            ret = self.device.read(0x81,32)
            self.brightnessing = False                                                
            return 

        if i > 0:   self.device.write(0x02,self.msg['brightness_light'],0)
        elif i < 0: self.device.write(0x02,self.msg['brightness_dark'],0)
        else:
            self.autobrightness()
            return
        self.brightnessing = True
        ret = self.device.read(0x81,32)

    def autobrightness(self):
        self.device.write(0x02,self.msg['brightness_auto'],0)
        ret = self.device.read(0x81,32)
    
    def autofocus(self):
        self.device.write(0x02,self.msg['focus_auto'],0) 
        ret = self.device.read(0x81,32)

    def version(self):
        self.device.write(0x02,self.msg['version'],0)
        ret = self.device.read(0x81,32)
        return ret
    
    def cleardevice(self):
        '''Clear the devices memory on endpoint 0x83'''
        while True:
            try:
                results = self.device.read(0x83, 512)
            except usb.core.USBError as e:
                if e.args[0] == 'Operation timed out' :
                    break # timeout means we are done

    def get_image(self):
        try:
            self.device.write(0x04, self.msg['picture'],0)
            tmp = self.device.read(0x83,32)
        except:
            self.cleardevice()
            return False

        # Every package has a defined length in byte 4/5 of the first 8 Bytes
        # which is used to read the whole package
        answer = []  

        # 0xfef8 is the maximum size of a package                           
        # if it is smaller => the last package and exit                                                               
        size = 0xfef8
        while size == 0xfef8:                                                         
            try:
                ret = self.device.read(0x83,512)                                               
                size = 256*ret[5]+ret[4]
                answer += ret[8:]+self.device.read(0x83,size)                                        
            except:
                self.cleardevice()
                return False

        return ''.join([chr(i) for i in answer])
