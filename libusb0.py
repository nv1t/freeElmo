
'''
    File :       libusb0.py
    Author:      Stephan Messligner
    Last change: 2012-01-15

    Simple ctypes wrapper for libusb-0.1

    All the original functions can be accessed by their original name:
        usb_open
        usb_set_configuration
        ...

    Some slightly higher level api is also provided, hiding most of
    the ctypes dependencies. Functions can be accesses by omitting
    the leading 'usb_':
        open
        set_configuration
        ...

    For device enumeration, the function get_device_list is provided,
    which returns a python list of libusb device struct instances for
    all available devices on the bus.

    Example:
    (assume a SMT-01 thermometer as first device):

    import libusb0 as usb
    ds = usb.get_device_list()
    if len(ds)>0 and \
       ds[0].descriptor.idVendor is 0x04D8 and \
       ds[0].descriptor.idProduct is 0xFBC3:
        h = usb.open(ds[0])
        usb.set_configuration(h, 1)
        usb.claim_interface(h, 0)
        usb.interrupt_write(h, 0x01, (0xFA,0xF2), 8)
        di = usb.create_buffer(8)
        usb.interrupt_read(h, 0x81, di, 8)
        print list(di)
        usb.close(h)
'''
#================================================================

# This file is based on the libubs-win32 header.
# Modifications for linux compatibility have been made where necessary.

#-----------------------------------------------
from ctypes import *
import ctypes.util
#-----------------------------------------------

# Some platform dependent stuff
import sys, os

class Struct(Structure):
    pass

if sys.platform=='win32':
    _libname = 'libusb0.dll'
    LIBUSB_PATH_MAX = 512
    Struct._pack_ = 1
    LIBUSB_HAS_GET_DRIVER_NP = 0
    LIBUSB_HAS_DETACH_KERNEL_DRIVER_NP = 0
elif sys.platform=='linux2':
    _libname = ctypes.util.find_library('usb-0.1')
    LIBUSB_PATH_MAX = os.pathconf('/',4)+1 
    LIBUSB_HAS_GET_DRIVER_NP = 1
    LIBUSB_HAS_DETACH_KERNEL_DRIVER_NP = 1
else: raise 'libusb0.py: Operating system not supported.'    


#================================================================
# Type definitions
#================================================================

#------- USB Device classes ---------
USB_CLASS_PER_INTERFACE = 0     # Device class specified per interface
USB_CLASS_AUDIO         = 1
USB_CLASS_COMM          = 2
USB_CLASS_HID           = 3
USB_CLASS_PRINTER       = 7
USB_CLASS_MASS_STORAGE  = 8
USB_CLASS_HUB           = 9
USB_CLASS_DATA          = 10
USB_CLASS_VENDOR_SPEC   = 0xFF

#------- USB Descriptor types ---------
USB_DT_DEVICE    = 0x01
USB_DT_CONFIG    = 0x02
USB_DT_STRING    = 0x03
USB_DT_INTERFACE = 0x04
USB_DT_ENDPOINT  = 0x05
USB_DT_HID       = 0x21
USB_DT_REPORT    = 0x22
USB_DT_PHYSICAL	 = 0x23
USB_DT_HUB       = 0x29

#------- Descriptor sizes -------------
USB_DT_DEVICE_SIZE         = 18
USB_DT_CONFIG_SIZE         = 9
USB_DT_INTERFACE_SIZE      = 9
USB_DT_ENDPOINT_SIZE       = 7
USB_DT_ENDPOINT_AUDIO_SIZE = 9
USB_DT_HUB_NONVAR_SIZE     = 7


 
#------- Descriptor header---------
# All standard descriptors have these 2 fields in common 
class usb_descriptor_header(Struct):
    _fields_ = [
        ('bLength',         c_ubyte ),
        ('bDescriptorType', c_ubyte ),  
    ]
    
#------- String descriptor ---------
class usb_string_descriptor(Struct):
    _fields_ = [            
        ('bLength',         c_ubyte ),
        ('bDescriptorType', c_ubyte ),
        ('wData[1]',        c_ushort )
    ]

#------- HID descriptor ---------
class usb_hid_descriptor(Struct):
    _fields_ = [
        ('bLength',         c_ubyte ),
        ('bDescriptorType', c_ubyte ),
        ('bcdHID',          c_ushort ),
        ('bCountryCode',    c_ubyte ),
        ('bNumDescriptors', c_ubyte ),
    ]

#------- Endpoint descriptor ---------
USB_MAXENDPOINTS = 32
class usb_endpoint_descriptor(Struct):
    _fields_ = [
        ('bLength',          c_ubyte ),
        ('bDescriptorType',  c_ubyte ),
        ('bEndpointAddress', c_ubyte ),
        ('bmAttributes',     c_ubyte ),
        ('wMaxPacketSize',   c_ushort ),
        ('bInterval',        c_ubyte ),
        ('bRefresh',         c_ubyte ),
        ('bSynchAddress',    c_ubyte ),
        ('extra',    POINTER(c_ubyte) ),
        ('extralen',         c_int )
    ]

USB_ENDPOINT_ADDRESS_MASK  = 0x0F    # in bEndpointAddress 
USB_ENDPOINT_DIR_MASK      = 0x80
USB_ENDPOINT_TYPE_MASK     = 0x03    # in bmAttributes 
USB_ENDPOINT_TYPE_CONTROL     = 0
USB_ENDPOINT_TYPE_ISOCHRONOUS = 1
USB_ENDPOINT_TYPE_BULK        = 2
USB_ENDPOINT_TYPE_INTERRUPT   = 3

#------- Interface descriptor ---------
USB_MAXINTERFACES = 32
class usb_interface_descriptor(Struct):
    _fields_ = [
        ('bLength',            c_ubyte ),
        ('bDescriptorType',    c_ubyte ),
        ('bInterfaceNumber',   c_ubyte ),
        ('bAlternateSetting',  c_ubyte ),
        ('bNumEndpoints',      c_ubyte ),
        ('bInterfaceClass',    c_ubyte ),
        ('bInterfaceSubClass', c_ubyte ),
        ('bInterfaceProtocol', c_ubyte ),
        ('iInterface',         c_ubyte ),
        ('endpoint', POINTER(usb_endpoint_descriptor) ),
        ('extra',      POINTER(c_ubyte) ),
        ('extralen',           c_int )
    ]

USB_MAXALTSETTING = 128
class usb_interface(Structure):
    _fields_ = [
        ('altsetting', POINTER(usb_interface_descriptor) ),
        ('num_altsetting', c_int)
    ]

#------- Configuration descriptor ---------
USB_MAXCONFIG = 8
class usb_config_descriptor(Struct):
    _fields_ = [
        ('bLength',         c_ubyte ),
        ('bDescriptorType', c_ubyte ),
        ('wTotalLength',    c_ushort ),
        ('bNumInterfaces',  c_ubyte ),
        ('bConfigurationValue', c_ubyte ),
        ('iConfiguration',  c_ubyte ),
        ('bmAttributes',    c_ubyte ),
        ('MaxPower',        c_ubyte ),
        ('interface', POINTER(usb_interface) ),
        ('extra',   POINTER(c_ubyte) ),
        ('extralen',        c_int )
    ]

#------- Device descriptor ---------------------
class usb_device_descriptor(Struct):
    _fields_ = [
        ('bLength',         c_ubyte),
        ('bDescriptorType', c_ubyte),
        ('bcdUSB',          c_ushort),
        ('bDeviceClass',    c_ubyte),
        ('bDeviceSubClass', c_ubyte),
        ('bDeviceProtocol', c_ubyte),
        ('bMaxPacketSize0', c_ubyte),
        ('idVendor',        c_ushort),
        ('idProduct',       c_ushort),
        ('bcdDevice',       c_ushort),
        ('iManufacturer',   c_ubyte),
        ('iProduct',        c_ubyte),
        ('iSerialNumber',   c_ubyte),
        ('bNumConfigurations', c_ubyte),
    ]

#------- USB Requests ---------------------
USB_REQ_GET_STATUS        = 0x00
USB_REQ_CLEAR_FEATURE     = 0x01
USB_REQ_SET_FEATURE       = 0x03
USB_REQ_SET_ADDRESS       = 0x05
USB_REQ_GET_DESCRIPTOR    = 0x06
USB_REQ_SET_DESCRIPTOR    = 0x07
USB_REQ_GET_CONFIGURATION = 0x08
USB_REQ_SET_CONFIGURATION = 0x09
USB_REQ_GET_INTERFACE     = 0x0A
USB_REQ_SET_INTERFACE     = 0x0B
USB_REQ_SYNCH_FRAME       = 0x0C
#       Request types
USB_TYPE_STANDARD = (0x00 << 5)
USB_TYPE_CLASS    = (0x01 << 5)
USB_TYPE_VENDOR   = (0x02 << 5)
USB_TYPE_RESERVED = (0x03 << 5)
#       Request recipients
USB_RECIP_DEVICE    = 0x00
USB_RECIP_INTERFACE = 0x01
USB_RECIP_ENDPOINT  = 0x02
USB_RECIP_OTHER     = 0x03
#       Endpoint directions (eq. request directions)
USB_ENDPOINT_IN     = 0x80
USB_ENDPOINT_OUT    = 0x00
 
#------- Device and bus structs  ---------------------
class usb_device(Struct):
    pass
                
class usb_bus(Struct):
    pass

usb_device._fields_ = [
        ('next', POINTER(usb_device) ),
        ('prev', POINTER(usb_device) ),
        ('filename', c_char * LIBUSB_PATH_MAX),
        ('bus', POINTER(usb_bus) ),
        ('descriptor', usb_device_descriptor ),
        ('config', POINTER(usb_config_descriptor) ),
        ('dev', c_void_p ),
        ('devnum', c_ubyte ),
        ('num_children', c_ubyte ),
        ('children', POINTER(POINTER(usb_device)) )
    ]

usb_bus._fields_ = [
        ('next', POINTER(usb_bus) ),
        ('prev', POINTER(usb_bus) ),
        ('dirname', c_char * LIBUSB_PATH_MAX),
        ('devices', POINTER(usb_device) ),
        ('location', c_ulong),
        ('root_dev', POINTER(usb_device) ),
    ]

#------- Device handle ------------
# Note: ptr to struct sometimes makes problems when passed to functions. Use void ptr instead.
usb_dev_handle_p = c_void_p

#================================================================
# Automatic error checking for library functions 
#================================================================

class LibusbError(Exception):
    'Generic Exception used for libusb errors.'
    def __init__(self, result, func, args):
        self.result = result
        self.func = func
        self.args = args
    def __str__(self):        
        msg = 'LibusbError in function %s%s:\n%d ' % \
                (self.func.__name__, str(self.args), self.result )
        msg += string_at(addressof(usb_strerror().contents))
        # :XXX: On linux, a timed out transfer returns ETIMEDOUT (-110) but
        # does not set strerror. On Darwin, 'No error' is 'no error'.
        return msg
    __repr__ = __str__
        
#---------------------------------------------------------------
# Most functions return a negative int in case of an error.
# In that case, raise an exception, passing information about the called function
# Otherwise, pass the result as python int.
def _errcheck(res, func, args):
    if res<0: raise LibusbError(res, func, args)
    return res
#---------------------------------------------------------------
# Some functions (usb_open, usb_device) return a Null pointer in case of an error.
# This seems to be implicitly converted to a None type by ctypes.
def _errcheck_ptr(res, func, args):
    #### print 'In _errcheck_ptr: res=%s, type=%s' % (str(res), str(type(res)))
    if res is None: raise LibusbError(res, func, args)
    return res

#================================================================    
# Function prototypes 
#================================================================

_lib = cdll.LoadLibrary(_libname)
_PROTOTYPE = CFUNCTYPE

#---------------------------------------------------------------
# usb.c
#---------------------------------------------------------------
# usb_dev_handle *usb_open(struct usb_device *dev);
# Note: ptr to struct sometimes is not recognized by ctypes. Use void ptr instead.
usb_open = \
    _PROTOTYPE( usb_dev_handle_p, c_void_p ) \
    ( ('usb_open', _lib),
      ( (1, "dev"), ) )
usb_open.__name__ = 'usb_open'
##usb_open.errcheck = _errcheck_ptr
#---------------------------------------------------------------
# int usb_close(usb_dev_handle *dev);
usb_close = \
    _PROTOTYPE( int, usb_dev_handle_p ) \
    ( ('usb_close', _lib),
      ( (1, "dev"), ) )
usb_close.__name__ = 'usb_close'
usb_close.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_get_string(usb_dev_handle *dev, int index, int langid, char *buf, size_t buflen);
usb_get_string = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_int, POINTER(c_char), c_size_t ) \
    ( ('usb_get_string', _lib),
      ( (1, "dev"), (1, "index"), (1, "langid"), (1, "buf"), (1, "buflen")  ) )
usb_get_string.__name__ = 'usb_get_string'
usb_get_string.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_get_string_simple(usb_dev_handle *dev, int index, char *buf, size_t buflen);
usb_get_string_simple = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, POINTER(c_char), c_size_t ) \
    ( ('usb_get_string_simple', _lib),
      ( (1, "dev"), (1, "index"), (1, "buf"), (1, "buflen")  ) )
usb_get_string.__name__ = 'usb_get_string'
usb_get_string.errcheck = _errcheck
#---------------------------------------------------------------
# descriptors.c
#---------------------------------------------------------------
# int usb_get_descriptor_by_endpoint(usb_dev_handle *udev, int ep, unsigned char type,
#                                    unsigned char index, void *buf, int size);
usb_get_descriptor_by_endpoint = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_ubyte, c_ubyte, c_void_p, c_int ) \
    ( ('usb_get_descriptor_by_endpoint', _lib),
      ( (1, "dev"), (1, "ep"), (1, "type"), (1, "index"), (1, "buf"), (1, "size")  ) )
usb_get_descriptor_by_endpoint.__name__ = 'usb_get_descriptor_by_endpoint'
usb_get_descriptor_by_endpoint.errcheck = _errcheck
#---------------------------------------------------------------
#    int usb_get_descriptor(usb_dev_handle *udev, unsigned char type,
#                           unsigned char index, void *buf, int size);
usb_get_descriptor = \
    _PROTOTYPE( int, usb_dev_handle_p, c_ubyte, c_ubyte, c_void_p, c_int ) \
    ( ('usb_get_descriptor', _lib),
      ( (1, "dev"), (1, "type"), (1, "index"), (1, "buf"), (1, "size")  ) )
usb_get_descriptor.__name__ = 'usb_get_descriptor'
usb_get_descriptor.errcheck = _errcheck
#---------------------------------------------------------------
# <arch>.c
# use c_void_p for all data buffers
#---------------------------------------------------------------
# int usb_bulk_write(usb_dev_handle *dev, int ep, char *bytes, int size, int timeout);
usb_bulk_write = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_void_p, c_int, c_int ) \
    ( ('usb_bulk_write', _lib),
      ( (1, "dev"), (1, "ep"), (1, "bytes"), (1, "size"), (1, "timeout")  ) )
usb_bulk_write.__name__ = 'usb_bulk_write'
usb_bulk_write.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_bulk_read(usb_dev_handle *dev, int ep, char *bytes, int size, int timeout);
usb_bulk_read = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_void_p, c_int, c_int ) \
    ( ('usb_bulk_read', _lib),
      ( (1, "dev"), (1, "ep"), (1, "bytes"), (1, "size"), (1, "timeout")  ) )
usb_bulk_read.__name__ = 'usb_bulk_read'
usb_bulk_read.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_interrupt_write(usb_dev_handle *dev, int ep, char *bytes, int size, int timeout);
usb_interrupt_write = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_void_p, c_int, c_int ) \
    ( ('usb_interrupt_write', _lib),
      ( (1, "dev"), (1, "ep"), (1, "bytes"), (1, "size"), (1, "timeout")  ) )
usb_interrupt_write.__name__ = 'usb_interrupt_write'
usb_interrupt_write.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_interrupt_read(usb_dev_handle *dev, int ep, char *bytes, int size, int timeout);
usb_interrupt_read = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_void_p, c_int, c_int ) \
    ( ('usb_interrupt_read', _lib),
      ( (1, "dev"), (1, "ep"), (1, "bytes"), (1, "size"), (1, "timeout")  ) )
usb_interrupt_read.__name__ = 'usb_interrupt_read'
usb_interrupt_read.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value,
#                        int index, char *bytes, int size, int timeout);
usb_control_msg = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int, c_int, \
                c_int, c_int, c_void_p, c_int, c_int ) \
    ( ('usb_control_msg', _lib),
      ( (1, "dev"), (1, "requesttype"), (1, "request"), (1, "value"),
        (1, "index"), (1, "bytes"), (1, "size"), (1, "timeout")  ) )
usb_control_msg.__name__ = 'usb_control_msg'
usb_control_msg.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_set_configuration(usb_dev_handle *dev, int configuration);
usb_set_configuration = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int ) \
    ( ('usb_set_configuration', _lib),
      ( (1, "dev"), (1, "configuration")  ) )
usb_set_configuration.__name__ = 'usb_set_configuration'
usb_set_configuration.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_claim_interface(usb_dev_handle *dev, int interface);
usb_claim_interface = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int ) \
    ( ('usb_claim_interface', _lib),
      ( (1, "dev"), (1, "interface")  ) )
usb_claim_interface.__name__ = 'usb_claim_interface'
usb_claim_interface.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_release_interface(usb_dev_handle *dev, int interface);
usb_release_interface = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int ) \
    ( ('usb_release_interface', _lib),
      ( (1, "dev"), (1, "interface")  ) )
usb_release_interface.__name__ = 'usb_release_interface'
usb_release_interface.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_set_altinterface(usb_dev_handle *dev, int alternate);
usb_set_altinterface = \
    _PROTOTYPE( int, usb_dev_handle_p, c_int ) \
    ( ('usb_set_altinterface', _lib),
      ( (1, "dev"), (1, "alternate")  ) )
usb_set_altinterface.__name__ = 'usb_set_altinterface'
usb_set_altinterface.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_resetep(usb_dev_handle *dev, unsigned int ep);
# (deprecated, use usb_clear_halt() instead )
#---------------------------------------------------------------
# int usb_clear_halt(usb_dev_handle *dev, unsigned int ep);
usb_clear_halt = \
    _PROTOTYPE( int, usb_dev_handle_p, c_uint ) \
    ( ('usb_clear_halt', _lib),
      ( (1, "dev"), (1, "ep")  ) )
usb_clear_halt.__name__ = 'usb_clear_halt'
usb_clear_halt.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_reset(usb_dev_handle *dev);
usb_reset = \
    _PROTOTYPE( int, usb_dev_handle_p ) \
    ( ('usb_reset', _lib),
      ( (1, "dev"),  ) )
usb_reset.__name__ = 'usb_reset'
usb_reset.errcheck = _errcheck
#---------------------------------------------------------------
# char *usb_strerror(void);
usb_strerror = \
    _PROTOTYPE( POINTER(c_char) ) \
    ( ('usb_strerror', _lib), None  )
usb_strerror.__name__ = 'usb_strerror'
usb_strerror.errcheck = _errcheck_ptr
#---------------------------------------------------------------
# void usb_init(void);
usb_init = \
    _PROTOTYPE( None ) \
    ( ('usb_init', _lib), None )
usb_init.__name__ = 'usb_init'
#---------------------------------------------------------------
# void usb_set_debug(int level);
usb_set_debug = \
    _PROTOTYPE( None, c_int ) \
    ( ('usb_set_debug', _lib),
      ( (1, "level"), ) )
usb_set_debug.__name__ = 'usb_set_debug'
#---------------------------------------------------------------
# int usb_find_busses(void);
usb_find_busses = \
    _PROTOTYPE( c_int ) \
    ( ('usb_find_busses', _lib), None )
usb_find_busses.__name__ = 'usb_find_busses'
usb_find_busses.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_find_devices(void);
usb_find_devices = \
    _PROTOTYPE( c_int ) \
    ( ('usb_find_devices', _lib), None )
usb_find_devices.__name__ = 'usb_find_devices'
usb_find_devices.errcheck = _errcheck
#---------------------------------------------------------------
# struct usb_device *usb_device(usb_dev_handle *dev);
usb_device_from_handle = \
    _PROTOTYPE( POINTER(usb_device), usb_dev_handle_p ) \
    ( ('usb_device', _lib),
      ( (1, "dev"),  ) )
usb_device_from_handle.__name__ = 'usb_device_from_handle'
usb_device_from_handle.errcheck = _errcheck_ptr
#---------------------------------------------------------------
# struct usb_bus *usb_get_busses(void);
usb_get_busses = \
    _PROTOTYPE( POINTER(usb_bus) ) \
    ( ('usb_get_busses', _lib), None )
usb_get_busses.__name__ = 'usb_get_busses'
usb_get_busses.errcheck = _errcheck

#---------------------------------------------------------------
# int usb_get_driver_np(usb_dev_handle *dev, int interface, char *name, unsigned int namelen);
# Platform dependent
if LIBUSB_HAS_GET_DRIVER_NP:
    usb_get_driver_np = \
        _PROTOTYPE( int, usb_dev_handle_p, c_int, c_char_p, c_uint ) \
        ( ('usb_get_driver_np', _lib),
          ( (1, "dev"), (1, "interface"), (1, "name"), (1, "namelen")  ) )
    usb_get_driver_np.__name__ = 'usb_get_driver_np'
    usb_get_driver_np.errcheck = _errcheck
#---------------------------------------------------------------
# int usb_detach_kernel_driver_np( usb_dev_handle *dev, int interface);
# Platform dependent
if LIBUSB_HAS_DETACH_KERNEL_DRIVER_NP:
    usb_detach_kernel_driver_np = \
        _PROTOTYPE( int, usb_dev_handle_p, c_int ) \
        ( ('usb_detach_kernel_driver_np', _lib),
          ( (1, "dev"), (1, "interface")  ) )
    usb_detach_kernel_driver_np .__name__ = 'usb_detach_kernel_driver_np'
    usb_detach_kernel_driver_np .errcheck = _errcheck



#================================================================
#  Medium level api, hide ctypes dependencies
#================================================================
# Init library now.
usb_init()
#---------------------------------------------------------------
# Open device. Accepts usb_device struct as well as ptr(usb_device)-
# For convenience: Immediately set configuration, interface and alternative
# after opening device
def open(dev, config=None, interface=None, alt=None):  
    if type(dev) is POINTER(usb_device):
        handle = usb_open( dev )    # Note: usb_open() expects a pointer to a usb_device struct
    elif type(dev) is usb_device:
        handle = usb_open( byref(dev) ) 
    else: raise TypeError('Expected %s, but got %s' % (str(usb_device), str(type(dev) ) ) )
    if config != None:
        detach_kernel_driver_np( handle, interface if interface!=None else 0)
        if config != get_configuration(handle):  # :NOTE: On linux, set_configuration hangs 
            set_configuration(handle, config)  # if trying to set the currently active conf. 
    if interface != None:
        detach_kernel_driver_np( handle, interface )
        claim_interface(handle, interface)
        if alt != None:
                set_altinterface(handle, alt)
    return handle
#---------------------------------------------------------------
close = usb_close
#---------------------------------------------------------------
reset = usb_reset
#---------------------------------------------------------------
# Get string descriptor as py-string
def get_string(hdev, index, langid=None):
    len = 128
    while(1):
        s = create_string_buffer(len)
        r = usb_get_string_simple(hdev, index, s, len)
        if r<=0: return None
        if r<len: return s.value
        len *= 2
# :TODO: 
# Distinguish between unicode/simple version by presence of language id parameter
# Return unicode string for langid!=0
#---------------------------------------------------------------
# :TODO: 
# Descriptor format depends on requested descriptor type.
# Must parse received data for configuration descriptor to
# extract interface and endpoint descriptors. Note however,
# that all standard descriptors can also be obtained from
# the usb_device struct via get_device_from_handle,
# eg. dev.config[0].interface[0].altsetting[0].endpoint[0].wMaxPacketSize
##    int usb_get_descriptor(usb_dev_handle *udev, unsigned char type,
##                           unsigned char index, void *buf, int size);
#---------------------------------------------------------------
# usb_get_descriptor_by_endpoint()
# Only needed for control endpoints != 0
#---------------------------------------------------------------
# Transfers
#----------------------------------------------------------------
# Helper function 
# Set default timeout for transfer calls 
_timeout = 5000
def set_timeout(timeout):
    _timeout = int(timeout)
#----------------------------------------------------------------
# Helper function
# Create a data buffer of <size> bytes
def create_buffer(size, data=()):
    return (c_ubyte*size)(*data)
create_data_buffer = create_buffer
#---------------------------------------------------------------
# Internal helper function:
# Convert data to ctypes buffer if necessary.
# For buffer arrays, if size>len(data) then zero-pad
def _prepare_data_buffer(data, size):
    if not size>0: size=len(data)   # Get size from buffer length if not specified
    if not \
        (isinstance(data, Array) and size<=len(data) or \
         isinstance(data, c_void_p) or \
         isinstance(data, c_char_p) ):  # ctypes pointer/array can be passed directly to function
        data = (c_ubyte*size)(*data)    # else must copy user data to a suitable buffer
    return data, size
#---------------------------------------------------------------
def bulk_write(hdev, endp, data, size=None, timeout=_timeout):
    _data, _size = _prepare_data_buffer(data,size)
    return usb_bulk_write(hdev, endp, _data, _size, timeout)
#---------------------------------------------------------------    
def bulk_read(hdev, endp, data, size=None, timeout=_timeout):
    _data, _size = _prepare_data_buffer(data,size)
    ret = usb_bulk_read(hdev, endp, data, size, timeout)
    if _data != data:           # Used intermediate buffer?
        data[0:ret] = _data[0:ret]    # Then copy data back to user buffer.
    return ret
#---------------------------------------------------------------
def interrupt_write(hdev, endp, data, size=None, timeout=_timeout):
    _data, _size = _prepare_data_buffer(data, size)
    return usb_interrupt_write(hdev, endp, _data, _size, timeout)
#---------------------------------------------------------------    
def interrupt_read(hdev, endp, data, size=None, timeout=_timeout):
    _data, _size = _prepare_data_buffer(data, size)
    ret = usb_interrupt_read(hdev, endp, data, size, timeout)
    if _data != data:           # Used intermediate buffer?
        data[0:ret] = _data[0:ret]    # Then copy data back to user buffer.
    return ret
#---------------------------------------------------------------    
def control_msg( hdev, requesttype, request, value, index, data,
                 size=None, timeout=_timeout):
    _data, _size = _prepare_data_buffer(data, size)
    ret = usb_control_msg( hdev, requesttype, request, value, index,
                           data, size, timeout)
    if (requesttype & USB_ENDPOINT_IN) \
       and (_data!=data):        # Used intermediate buffer for input request?
        data[0:ret] = _data[0:ret]  # Must copy data to user buffer
#---------------------------------------------------------------
# Set configuration
set_configuration = usb_set_configuration
#---------------------------------------------------------------
# Get active configuration (not provided by libusb)
def get_configuration( hdev ): 
    conf = c_byte()
    usb_control_msg( hdev, USB_ENDPOINT_IN, USB_REQ_GET_CONFIGURATION, 
                     0, 0, byref(conf), 1, _timeout ) 
    return conf.value
#---------------------------------------------------------------
# Claim interface
claim_interface = usb_claim_interface
#---------------------------------------------------------------
# Release interface
release_interface = usb_release_interface
#---------------------------------------------------------------
# Set interace alternative
set_altinterface = usb_set_altinterface
#---------------------------------------------------------------
# Clear_feature(endpoint_halt). Resets endpoint.
clear_halt = usb_clear_halt
#---------------------------------------------------------------
# Reset device
reset = usb_reset
# :TODO: Auto re-open device?
#---------------------------------------------------------------
# Get last error message
def strerror():
    return string_at( addressof(usb_strerror().contents) ) # Cast to py-string
#---------------------------------------------------------------
# Init library
init = usb_init
#---------------------------------------------------------------
# Set debug level
set_debug = usb_set_debug
#---------------------------------------------------------------
# Enumerate busses and devices
find_busses = usb_find_busses
find_devices = usb_find_devices
#---------------------------------------------------------------
# Get corresponding device struct from handle
# :TODO: Find out: are structs deep-copied?
def device_from_handle( hdev ):
    return usb_device_from_handle(hdev).contents
#---------------------------------------------------------------
# struct usb_bus *usb_get_busses(void);
def get_busses():
    usb_find_busses()
    usb_find_devices()
    return usb_get_busses().contents
#---------------------------------------------------------------
# Helper function
# Compile a list of available devices
def get_device_list(idVendor=None, idProduct=None, bcdDevice=None):
    usb_init()
    all_devices = []
    usb_find_busses()
    usb_find_devices()
    bus = usb_get_busses()
    #Get all devices
    while bus:
        dev = bus.contents.devices
        while dev:
            all_devices.append(dev.contents)
            dev = dev.contents.next
        bus = bus.contents.next
    #Select devices
    device_list = []
    for dev in all_devices:
        if (idVendor==None or idVendor==dev.descriptor.idVendor) and\
           (idProduct==None or idProduct==dev.descriptor.idProduct) and\
           (bcdDevice==None or bcdDevice==dev.descriptor.bcdDevice):
            device_list.append( dev )
    #:TODO: Add other selection fields, eg.
    #       Device class, inter
    #       Serial number string (need to open device for that)    
    return device_list
#---------------------------------------------------------------
def get_driver_np( hdev, interface ):
    if not LIBUSB_HAS_GET_DRIVER_NP:
        return None
    slen = 128
    while(1):
        s = create_string_buffer(slen)
        try: usb_get_driver_np(hdev, interface, s, slen-1)
        except LibusbError as usberr:
            if usberr.result == -61: # Will return error code 61 if no driver is attached
                return None
            else: raise
        name = string_at( addressof(s) )
        if len(name)<slen: return name
        slen *= 2
get_driver = get_driver_np
#---------------------------------------------------------------
def detach_kernel_driver_np( hdev, interface ):
    if not  LIBUSB_HAS_DETACH_KERNEL_DRIVER_NP:
        return 0
    try: return usb_detach_kernel_driver_np( hdev, interface )
    except LibusbError as usberr:
        if usberr.result == -61:  # Will return error code 61 if no driver is attached
            return -61            # Do not regard this as an error here
        else: raise
detach_kernel_driver = detach_kernel_driver_np
#---------------------------------------------------------------

