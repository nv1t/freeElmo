import pygame, sys, datetime, os
from pygame.locals import *
from PIL import Image
import cStringIO as StringIO
import elmo
#import helper functions
from elmoDisplayHelpers import render_textrect
from elmoDisplayHelpers import Button

pygame.init() #init pygame

########################
# set fonts and colors #
########################
#fonts:
basic_font = ""
basic_font_size = 100
help_font_size = 100
buttons_font_size = 100
#colors:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LGRAY = (216, 216, 216)
DGRAY = (48, 48, 48)

###############
# global vars #
###############
version = "0.6.5"
info = pygame.display.Info()
fullscreen = False
rotate = False
rotate_90 = 0
rotate_90_changed = False
display_help = False
display_interface = False
image_res = None
image_size = None
image = None
screen_res = None
screen = None
cam_connect = -1
error_no_elmo = True
error_no_image = True
buttons = {}

#############
# functions #
#############
#draw help-window with commands on the screen 
def draw_help(screen, screen_size, version, font, font_size, color_background, color_font):
    #define string to display 
    my_string = """\n
                Help\n
                Quit: Ctrl+Q, Alt+F4, Escape\n
                Display Help: Ctrl+H, F1  
                Exit Help: Ctrl+H, F1, Escape\n
                Show/Hide Interface: Crtl+I\n
                Toggle Fullscreen: Ctrl+F
                Rotate Image 180 Degree: Ctrl+T"""
                   #Rotate Image 90 Degree: Ctrl+R\n
    my_string += """\n
                Save Image: Ctrl+S\n\n
                Camera options:\n
                Zoom in start/stop: Ctrl+C
                Zoom out start/stop: Ctrl+V\n
                Reset Brightness: Ctrl+G 
                Brightness up start/stop: Ctrl+D
                Brightness down start/stop: Ctrl+X\n
                Autofocus: Ctrl+A
                Macrofocus start/stop: Ctrl+E
                Widefocus start/stop: Ctrl+W\n\n
                Free ELMO - Version """+version+"""
                (c)2013 nuit & McSumo"""
    #define resolution of the rectangle
    height = screen_size[1] - 100
    if height < 200:
        height = 200
    width= (height/5)*4
    #create rectangle
    textRect = pygame.Rect((0, 0, width, height))
    #set rectangle position to middle of the screen
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery   
    fits = False
    while not fits:
        try:
            #render the text for the rectangle
            rendered_text = render_textrect(my_string, pygame.font.SysFont(font, font_size), textRect, color_font, color_background, 0)
            fits = True
        except:
            font_size = font_size - 1
            if font_size == 1:
                fits = True
    if rendered_text:
        screen.blit(rendered_text, textRect)
    return [screen, font_size]
        
#draw a interface with buttons on the screen        
def draw_interface(screen, screen_size, buttons, error_no_elmo, font, font_size, color_background, color_font, bold=False):
    #the screen will be split in a relative size for the adjustable buttons size
    #it will be the same a in help a minimum resolution of 200x200 pixels is standard
    #calculate relative size of tides for the screen
    if screen_size[1] > 200:
        screen_height = screen_size[1]
    else:
        screen_height = 200
    font_size = (screen_height/20)/2
    button_width = 6 * font_size
    button_height = 1 * font_size
    #Create buttons Array
    buttons = {}
    #Parameters for Buttons: surface, color, x, y, length, height, width, text, text_color, font, font_size, bold
    buttons["exit"] = Button()
    buttons["exit"].create_button(screen, color_background, 0, 0*button_height, button_width, button_height, 0, "Exit", color_font, font, font_size, bold)
    buttons["help"] = Button()
    buttons["help"].create_button(screen, color_background, 0, 2*button_height, button_width, button_height, 0, "Help", color_font, font, font_size, bold)
    buttons["interface"] = Button()
    buttons["interface"].create_button(screen, color_background, 0, 4*button_height, button_width, button_height, 0, "Interface Off", color_font, font, font_size, bold)
    buttons["fullscreen"] = Button()
    buttons["fullscreen"].create_button(screen, color_background, 0, 6*button_height, button_width, button_height, 0, "Fullscreen", color_font, font, font_size, bold)
    buttons["rotate"] = Button()
    buttons["rotate"].create_button(screen, color_background, 0, 8*button_height, button_width, button_height, 0, "Rotate Image", color_font, font, font_size, bold)
    buttons["save"] = Button()
    buttons["save"].create_button(screen, color_background, 0, 10*button_height, button_width, button_height, 0, "Save Image", color_font, font, font_size, bold)
    #Deactivation of elmo-systems-commands if the elmo-device is not connected
    if error_no_elmo == False:
        buttons["zoom_in"] = Button()
        buttons["zoom_in"].create_button(screen, color_background, 0, 12*button_height, button_width, button_height, 0, "Zoom In", color_font, font, font_size, bold)
        buttons["zoom_out"] = Button()
        buttons["zoom_out"].create_button(screen, color_background, 0, 14*button_height, button_width, button_height, 0, "Zoom Out", color_font, font, font_size, bold)
        buttons["brightness_reset"] = Button()
        buttons["brightness_reset"].create_button(screen, color_background, 0, 16*button_height, button_width, button_height, 0, "Reset Brightness", color_font, font, font_size, bold)
        buttons["brightness_up"] = Button()
        buttons["brightness_up"].create_button(screen, color_background, 0, 18*button_height, button_width, button_height, 0, "Brightness Up", color_font, font, font_size, bold)
        buttons["brightness_down"] = Button()
        buttons["brightness_down"].create_button(screen, color_background, 0, 20*button_height, button_width, button_height, 0, "Brightness Down", color_font, font, font_size, bold)
        buttons["focus_auto"] = Button()
        buttons["focus_auto"].create_button(screen, color_background, 0, 22*button_height, button_width, button_height, 0, "Autofocus", color_font, font, font_size, bold)
        buttons["focus_macro"] = Button()
        buttons["focus_macro"].create_button(screen, color_background, 0, 24*button_height, button_width, button_height, 0, "Macrofocus", color_font, font, font_size, bold)
        buttons["focus_wide"] = Button()
        buttons["focus_wide"].create_button(screen, color_background, 0, 26*button_height, button_width, button_height, 0, "Widefocus", color_font, font, font_size, bold)
    return [buttons, font_size]

#toggle the fullscreen state
def toggle_fullscreen(image, screen, fullscreen, image_res):
    if fullscreen:
        screen = pygame.display.set_mode(screen_res, RESIZABLE)
        fullscreen = False 
    else:
        try:
            screen = pygame.display.set_mode(image_res, FULLSCREEN)
            fullscreen = True
        except:
            string = "\n   Can't change to fullscreen.\n   No video mode isn't large enough for the image resolution.\n"
            textRect = pygame.Rect((10, 10, 500, 65))
            rendered_text = render_textrect(string, pygame.font.SysFont("", 24), textRect, LGRAY, DGRAY, 0)
            if rendered_text:
                screen.blit(rendered_text, textRect)        
            pygame.display.update()
            fullscreen = False
    return [screen, fullscreen]

#get image format
def get_image_format(image):
    size = image.get_size()
    if (size[0]/4)*3*0.95 < size[1] and size[1] < (size[0]/4)*3*1.05:
        format = [4, 3]
    elif (size[0]/3)*4*0.95 < size[1] and size[1] < (size[0]/3)*4*1.05:
        format = [3, 4]
    elif (size[0]/5)*4*0.95 < size[1] and size[1] < (size[0]/5)*4*1.05:
        format = [5, 4]
    elif (size[0]/4)*5*0.95 < size[1] and size[1] < (size[0]/4)*5*1.05:
        format = [4, 5]
    elif (size[0]/16)*10*0.95 < size[1] and size[1] < (size[0]/16)*10*1.05:
        format = [16, 10]
    elif (size[0]/10)*16*0.95 < size[1] and size[1] < (size[0]/10)*16*1.05:
        format = [10, 16]
    elif (size[0]/9)*16*0.95 < size[1] and size[1] < (size[0]/9)*16*1.05:
        format = [9, 16]
    else:
        format = [16, 9]
    return format
        
#resize image
def resize_image(image, screen):
    #calculate actual sizes 
    format = get_image_format(image)
    screen_size = screen.get_size()
    image_size = image.get_size()
    #calculate the new image size
    if screen_size[0]/format[0] > screen_size[1]/format[1]:
        height = screen_size[1]
        width = (height/format[1])*format[0]
    elif screen_size[0]/format[0] == screen_size[1]/format[1]:
        width = screen_size[0]
        height = screen_size[1]
    elif screen_size[0]/format[0] < screen_size[1]/format[1]:
        width = screen_size[0]
        height = (width/format[0])*format[1]   
    return [width, height]

#get the padding for .blit(image, (x,y))
def get_image_padding(image, screen):
    screen_size = screen.get_size()
    image_size = image.get_size()
    x = (screen_size[0]-image_size[0])/2
    y = (screen_size[1]-image_size[1])/2
    return [x, y]

#save screen from actual image
def save_screen(screen):
    is_windows = sys.platform.startswith('win')
    if is_windows:
        dir_sep = "\\"
    else:
        dir_sep = "/"
    directory = "ELMO-Screenshots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    pygame.image.save(screen, "ELMO-Screenshots" + dir_sep + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png")

#reduce source to display resolution
def reduce_to_screen_size(image, info):
    image_size = image.get_size()
    #compare sizes an get a little extra space for taskbars to fit the image
    if image_size[0] > info.current_w:
        max_width = info.current_w - 100
    else:
        max_width = image_size[0] - 100
    if image_size[1] > info.current_h:
        max_height = info.current_h - 100
    else:
        max_height = image_size[1] - 100
    #reduce the screen to the format of the image
    format = get_image_format(image)
    if max_width > (max_height/format[1])*format[0]:
        max_width = (max_height/format[1])*format[0]
    if max_height > (max_width/format[0])*format[1]:
        max_height = (max_width/format[0])*format[1]
    return [max_width, max_height]
    
##########
# events #
##########
def events():
    #get global vars
    #vars are global because input and output changed too often => should be changed to input args and returns
    global elmo
    global cam
    global error_no_elmo
    global screen
    global image
    global fullscreen
    global rotate
    global rotate_90
    global display_help
    global display_interface
    global image_size
    global buttons
    global basic_font_size
    global help_font_size
    global buttons_font_size
    #button-pressed event-handling
    for event in pygame.event.get():
        #window resize event
        if event.type == pygame.VIDEORESIZE and fullscreen == False and error_no_elmo == False:
            size = event.size
            help_font_size = 100
            basic_font_size = 100
            buttons_font_size = 100
            screen = pygame.display.set_mode(size,RESIZABLE)
            try:
                if image != None:
                    image_size = resize_image(image, screen)
            except NameError:
                pass                
        #close program
        if event.type == pygame.QUIT:
            sys.exit()
        #keydown-events
        if event.type == pygame.KEYDOWN:
            #close program
            if (event.key == pygame.K_q and pygame.K_LCTRL) or (event.key == pygame.K_q and pygame.K_RCTRL) or (event.key == pygame.K_F4 and pygame.K_LALT) or (event.key == pygame.K_F4 and pygame.K_RALT) or (event.key == pygame.K_ESCAPE and display_help == False):
                sys.exit()    
            #toggle fullscreen
            if (event.key == pygame.K_f and pygame.K_LCTRL) or (event.key == pygame.K_f and pygame.K_RCTRL):
                results = toggle_fullscreen(image, screen, fullscreen, image_res)
                screen = results[0]
                fullscreen = results[1]
            #rotate display
            if (event.key == pygame.K_t and pygame.K_LCTRL) or (event.key == pygame.K_t and pygame.K_RCTRL):
                rotate = not rotate
            if (event.key == pygame.K_r and pygame.K_LCTRL) or (event.key == pygame.K_r and pygame.K_RCTRL):                    
                rotate_90 = rotate_90 + 1
                if rotate_90 == 4:
                    rotate_90 = 0
            #display help
            if (event.key == pygame.K_h and pygame.K_LCTRL) or (event.key == pygame.K_h and pygame.K_RCTRL) or event.key == pygame.K_F1:
                display_help = not display_help
            #display interface
            if (event.key == pygame.K_i and pygame.K_LCTRL) or (event.key == pygame.K_i and pygame.K_RCTRL):
                display_interface = not display_interface
            #make screenshot
            if (event.key == pygame.K_s and pygame.K_LCTRL) or (event.key == pygame.K_s and pygame.K_RCTRL):
                save_screen(image)
            #exit help with escape
            if event.key == pygame.K_ESCAPE and display_help == True:
                display_help = False
            #ELMO-Functions like zoom, brightness, focus
            if error_no_elmo == False:
                #zoom in
                if (event.key == pygame.K_c and pygame.K_LCTRL) or (event.key == pygame.K_c and pygame.K_RCTRL):
                    cam.zoom(1)
                #zoom out
                if (event.key == pygame.K_v and pygame.K_LCTRL) or (event.key == pygame.K_v and pygame.K_RCTRL):
                    cam.zoom(-1)
                #brightness up
                if (event.key == pygame.K_d and pygame.K_LCTRL) or (event.key == pygame.K_d and pygame.K_RCTRL):
                    cam.brightness(1)
                #brightness down
                if (event.key == pygame.K_x and pygame.K_LCTRL) or (event.key == pygame.K_x and pygame.K_RCTRL):
                    cam.brightness(-1)                
                #reset brightness
                if (event.key == pygame.K_g and pygame.K_LCTRL) or (event.key == pygame.K_g and pygame.K_RCTRL):
                    cam.brightness(0)
                #autofocus
                if (event.key == pygame.K_a and pygame.K_LCTRL) or (event.key == pygame.K_a and pygame.K_RCTRL):
                    cam.focus(0)
                #macro focus
                if (event.key == pygame.K_e and pygame.K_LCTRL) or (event.key == pygame.K_e and pygame.K_RCTRL):
                    cam.focus(-1)
                #wide focus
                if (event.key == pygame.K_w and pygame.K_LCTRL) or (event.key == pygame.K_w and pygame.K_RCTRL):
                    cam.focus(1)
        #Button handling
        elif event.type == MOUSEBUTTONDOWN:
            if buttons['exit'].pressed(pygame.mouse.get_pos()):
                sys.exit()
            if buttons['help'].pressed(pygame.mouse.get_pos()):
                display_help = not display_help
            if buttons['interface'].pressed(pygame.mouse.get_pos()):
                display_interface = not display_interface
            if buttons['fullscreen'].pressed(pygame.mouse.get_pos()):
                results = toggle_fullscreen(image, screen, fullscreen, image_res)
                screen = results[0]
                fullscreen = results[1]
            if buttons['rotate'].pressed(pygame.mouse.get_pos()):
                rotate = not rotate
            if buttons['save'].pressed(pygame.mouse.get_pos()):
                save_screen(image)
            #ELMO-Functions like zoom, brightness, focus
            if error_no_elmo == False:
                if buttons['zoom_in'].pressed(pygame.mouse.get_pos()):
                    cam.zoom(1)
                if buttons['zoom_out'].pressed(pygame.mouse.get_pos()):
                    cam.zoom(-1)
                if buttons['brightness_reset'].pressed(pygame.mouse.get_pos()):
                    cam.brightness(0)
                if buttons['brightness_up'].pressed(pygame.mouse.get_pos()):
                    cam.brightness(1)
                if buttons['brightness_down'].pressed(pygame.mouse.get_pos()):
                    cam.brightness(-1)
                if buttons['focus_auto'].pressed(pygame.mouse.get_pos()):
                    cam.focus(0)
                if buttons['focus_macro'].pressed(pygame.mouse.get_pos()):
                    cam.focus(-1)
                if buttons['focus_wide'].pressed(pygame.mouse.get_pos()):
                    cam.focus(1)

#################
# main-function #
#################
while 1:
    #################################
    # initialisation of ELMO device #
    #################################
    if error_no_elmo == True:
        try:    
            cam = elmo.Elmo()
            cam_connect = cam.connect()
            error_no_elmo = True if cam_connect == -1 else False
        except:
            error_no_elmo = True
            
    #### IMPORTANT!!! ####
    # The order of the elements is important so be careful with changes
    ######################
    #check for pygame events
    events()
    
    #clear background
    try:
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill(BLACK)
        screen.blit(background, (0, 0))
    except:
        pass
    try: 
        #get the image        
        data = cam.get_image()
        
        #make image to a pygame compatible
        stream = StringIO.StringIO(data)                                    
        image_new = Image.open(stream)
        
        #test:
        #image_new = Image.open("test3.jpg")
        #error_no_elmo = False
        #:test

        #rotate image x-90 degree
        #long calculation phases for the pictures, deactivated at the moment
        #image_new = image_new.rotate(90*(rotate_90%4))
        
        #draw image on screen
        image_new = pygame.image.fromstring(image_new.tostring(), image_new.size, image_new.mode)
        
        error_no_image = False
    except:
        #ELMO-Device wont deliver a image
        error_no_image = True
  
    #if new image update the image, else the old image will be displayed.
    if error_no_image == False:
        image = image_new

    if image != None:        
        #save of the image resolution
        image_res = image.get_size()

        #init display on startup if not set
        if screen is None:
            start_size = reduce_to_screen_size(image, info)
            screen = pygame.display.set_mode(start_size,RESIZABLE)
            pygame.display.set_caption(str("Free ELMO Version " + version)) #set msg of the window
            screen_res = screen.get_size()
            image_size = image.get_size()
            
        #rotate screen if demanded
        if rotate:
            image = pygame.transform.flip(image, True, True)
        
        #resize image to fit the screen
        if fullscreen == False:
            image_size = resize_image(image, screen) #not sure if it must before the if
            #resize the image
            image = pygame.transform.smoothscale(image, image_size)
            screen_res = screen.get_size()

        #draw image on screen
        screen.blit(image, get_image_padding(image,screen))
        
        #display help when ctrl+h, for close ctrl+h or esc must be pressed
        #must be after screen.blit(image...
        if display_help:
            help_returns = draw_help(screen, screen_res, version, basic_font, help_font_size, DGRAY, LGRAY) 
            screen = help_returns[0]
            help_font_size = help_returns[1]
        #display button-interface and return the buttons for event handling
        if display_interface:
            interface_returns = draw_interface(screen, screen_res, buttons, error_no_elmo, basic_font, buttons_font_size, DGRAY, LGRAY)
            buttons = interface_returns[0]
            buttons_font_size = interface_returns[1]
        #display error massage when no image is delivered
        if error_no_image:
            string = "\n   Can't get a new image.\n"
            textRect = pygame.Rect((10, 10, 200, 50))
            rendered_text = render_textrect(string, pygame.font.SysFont("", 24), textRect, LGRAY, DGRAY, 0)
            if rendered_text:
                screen.blit(rendered_text, textRect)        
    
    if error_no_elmo == True or image == None:
        if screen_res == None:
            screen_res = [400, 300]
        screen = pygame.display.set_mode(screen_res,RESIZABLE)
        pygame.display.set_caption(str("ERROR!!! - Free ELMO Version " + version)) #set msg of the window
        #define string to display
        error_string = ""
        if error_no_elmo:
            error_string = error_string + "\n\n    No Camera found    "
        if error_no_image:
            error_string = error_string + "\n\n    Didn't get a Image "
        #create rectangle
        textRect = pygame.Rect((0, 0, screen_res[0], screen_res[1]))
        #set rectangle position to middle of the screen
        textRect.centerx = screen.get_rect().centerx
        textRect.centery = screen.get_rect().centery  
        
        #render the text for the rectangle
        rendered_text = render_textrect(error_string, pygame.font.SysFont("", 24), textRect, LGRAY, DGRAY, 0)
        if rendered_text:
            screen.blit(rendered_text, textRect)

    pygame.display.update()
