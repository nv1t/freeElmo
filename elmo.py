import libusb0 as usb
from PIL import Image
import cStringIO as StringIO                                                    
import sys

class Elmo:
    def __init__(self):
        self.msg = {
            'version': [0,0,0,0,0x18,0,0,0,0x10,0x8B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            'picture': [0,0,0,0,0x18,0,0,0,0x8e,0x80,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            'buttons': [0,0,0,0,24,0,0,0,0,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        }
        self.last_image = None #Image.open("error.png")
        self._handle = None
        self.connect()

        return self

    def __del__(self):
        self.close()

    def connect(self,vendor=0x09a1,product=0x001d):
        if self._handle != None:
            self.close()
   
        for dev in usb.get_device_list(): 
            desc = dev.descriptor 
            if desc.idVendor==vendor and desc.idProduct==product):
                handle = usb.open(dev)  # Need to open the device to query string descriptors
                try:                                                        
                    usb.set_configuration( handle, 1 ) 
                    usb.claim_interface( handle, 0 ) 
                    self._handle = handle 

                    return                                              
                except:                                                     
                    usb.close(handle) 
                    raise 
        raise Exception('Device not found.') 

        return self

    def close(self):
        if self._handle != None:
            usb.close( self._handle )
            self._handle = None

    def _write(self, ep_out, data ):
        """ Write raw data to the device. Data should be list-like or a single integer.
            Data is automatically cropped or filled to the required endpoint size.  """
        if self._handle is None: 
            raise Exception("Invalid device.") 
        try: iter(data)      # Try to iterate. 
        except TypeError: 
            data = (data,)  # Convert to tuple. 
        usb.interrupt_write( self._handle, ep_out, bytearray(data), len(data) )

    def _read(self,ep_in,size_in): 
        """ Read raw data from the device.""" 
        if self._handle is None:
            raise Exception("Invalid device") 
        data = usb.create_data_buffer(size_in)
        usb.interrupt_read( self._handle, ep_in, data, size_in )
        return bytearray(data)

    def version(self):
        self._write(0x02,self.msg('version'))
        return self._read(0x81,32)
    
    def get_image(self):
        # Try to read a picture until you get a valid stream
        try:
            self._write(0x04,self.msg('picture'))
            tmp = self._read(0x83,32)
        except:
            #self.cleardevice()
            return self.last_image

        # Every package has a defined length in byte 4/5 of the first 8 Bytes
        # which is used to read the whole package
        finished = False                                                            
        error = False
        answer = []                                                                 
        while not finished:                                                         
            try:
                ret = self._read(0x83,512)                                               
                size = 256*ret[5]+ret[4]#-(512-8) # Byte to integer 
                answer += ret[8:]
                answer += self._read(0x83,size)                                        
            except:
                error = True
                return self.last_image
                break
            # 0xfef8 is the maximum size of a package
            # if it is smaller => the last package and exit
            if not size == 0xfef8:                                                  
                finished = True                                                     

        if not error:
            data = ''.join([chr(i) for i in answer])
            try:
                stream = StringIO.StringIO(data)
                image = Image.open(stream)
                #pg_image = pygame.image.fromstring(image.tostring(), image.size, image.mode)
                self.last_image = image
            except:
                pass
                #self.cleardevice()
            return self.last_image
