import pygame, sys, datetime, os
import pygame.camera
from pygame.locals import *
from PIL import Image
import elmo

pygame.init() #init pygame

##############
# external code for multiline text wordwrap:
# (c) Author: David Clark (da_clark (at) shaw.ca), date: May 23, 2001
### begin: ###
def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    import pygame
    
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface
#### :end ####

########################
# set fonts and colors #
########################
#fonts:
basicFont = pygame.font.SysFont(None, 24)
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
version = "0.5.6"
info = pygame.display.Info()
fullscreen = False
rotate = False
rotate_90 = 0
rotate_90_changed = False
display_help = False
display_interface = False
image_res = None
image_size = None
screen_res = None
screen = None
cam_connect = -1
error_no_elmo = False
error_no_image = False

#############
# functions #
#############
#draw help-window with commands on the screen 
def draw_help(screen):
    global basicFont
    global LGRAY
    global DGRAY 
    global version
    #define string to display 
    my_string = "\n                               Help\n\n  Quit: Ctrl+Q, Alt+F4, Escape\n\n  Display Help: Ctrl+H, F1\n  Exit Help: Ctrl+H, F1, Escape\n\n  Toggle Fullscreen: Ctrl+F\n\n  Rotate Image: Ctrl+R\n  Rotate Image 90 Degree: Ctrl+D\n\n  Save Image: Ctrl+S\n\n  Free ELMO - Version "+version+"\n  (c)2013 nuit & McSumo\n\n"
    #create rectangle
    textRect = pygame.Rect((0, 0, 400, 400))
    #set rectangle position to middle of the screen
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery   
    #render the text for the rectangle
    rendered_text = render_textrect(my_string, basicFont, textRect, LGRAY, DGRAY, 0)
    if rendered_text:
        screen.blit(rendered_text, textRect)

#toggle the fullscreen state
def toggle_fullscreen():
    global info
    global screen
    global image
    global fullscreen
    global image_res
    #info = pygame.display.Info()
    if fullscreen:
        #screen = pygame.display.set_mode((info.current_w,info.current_h), RESIZABLE)
        screen = pygame.display.set_mode(screen_res, RESIZABLE)
        fullscreen = False 
    else:
        try:
            #screen = pygame.display.set_mode((info.current_w,info.current_h), FULLSCREEN)
            screen = pygame.display.set_mode(image_res, FULLSCREEN)
            fullscreen = True
        except:
            string = "\n   Can't change to fullscreen.\n   No video mode isn't large enough for resolution.\n"
            textRect = pygame.Rect((10, 10, 400, 65))
            rendered_text = render_textrect(string, basicFont, textRect, LGRAY, DGRAY, 0)
            if rendered_text:
                screen.blit(rendered_text, textRect)        
            pygame.display.update()
            fullscreen = False

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
    elif (size[0]/9)*16*0.95 < size[1] and size[1] < (size[0]/9)*16*1.05:
        format = [5, 4]
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
def reduce_to_screen_size(image):
    global info
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
    #var definitions
    global screen
    global image
    global fullscreen
    global rotate
    global rotate_90
    global display_help
    global display_info
    global image_size
    #button-pressed event-handling
    #not working for fast event reload
    #pressed = pygame.key.get_pressed() #get the pressed keys
    #alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT] #set if left or rigth alt is pressed
    #ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL] #set if left or rigth ctrl is pressed
    for event in pygame.event.get():
        #window resize event
        if event.type == pygame.VIDEORESIZE and fullscreen == False and error_no_elmo == False:
            size = event.size
            screen = pygame.display.set_mode(size,RESIZABLE)
            try:
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
                toggle_fullscreen()
            #rotate display
            if (event.key == pygame.K_r and pygame.K_LCTRL) or (event.key == pygame.K_r and pygame.K_RCTRL):
                rotate = not rotate
            if (event.key == pygame.K_d and pygame.K_LCTRL) or (event.key == pygame.K_d and pygame.K_RCTRL):                    
                rotate_90 = rotate_90 + 1
                if rotate_90 == 4:
                    rotate_90 = 0
            #display help
            if (event.key == pygame.K_h and pygame.K_LCTRL) or (event.key == pygame.K_h and pygame.K_RCTRL) or event.key == pygame.K_F1:
                display_help = not display_help
            #make screenshot
            if (event.key == pygame.K_s and pygame.K_LCTRL) or (event.key == pygame.K_s and pygame.K_RCTRL):
                save_screen(image)
            #exit help with escape
            if event.key == pygame.K_ESCAPE and display_help == True:
                display_help = False

#################
# main-function #
#################
while 1:
    #################################
    # initialisation of ELMO device #
    #################################
    if cam_connect == -1:
        try:    
            #camera module for testing
            #pygame.camera.init()
            #cam = pygame.camera.Camera(0)
            #cam.start() 
            cam = elmo.Elmo()
            cam_connect = cam.connect()
            elmo_not_found = True if cam_connect == -1 else False
        except:
            elmo_not_found = True
            
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
        image = cam.get_image()
        
        #test:
        #image = Image.open("test.jpg")
        #cam_connect = 1
        #:test
        
        image = pygame.image.fromstring(image.tostring(), image.size, image.mode)
        
        error_no_image = False
    except:
        #ELMO-Device wont deliver a image
        error_no_image = True
    
    if not error_no_image:
        #save of the image resolution
        image_res = image.get_size()

        #init display on startup if not set
        if screen is None:
            start_size = reduce_to_screen_size(image)
            screen = pygame.display.set_mode(start_size,RESIZABLE)
            pygame.display.set_caption(str("Free ELMO Version " + version)) #set msg of the window
            screen_res = screen.get_size()
            image_size = image.get_size()
            
        #rotate screen if demanded
        if rotate:
            image = pygame.transform.flip(image, True, True)
        #rotate screen for x*90 degree
        image = pygame.transform.rotate(image, 90*(rotate_90%4))
        
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
            draw_help(screen)
        
    if error_no_elmo or error_no_image:
        error_no_elmo = False
        if screen_res == None:
            screen_res = [540, 400]
        screen = pygame.display.set_mode(screen_res,RESIZABLE)
        pygame.display.set_caption(str("ERROR!!! - Free ELMO Version " + version)) #set msg of the window
        #define string to display
        error_string = ""
        if error_no_elmo:
            error_string = error_string + "\n\n    No Camera found    \n\n"
        if error_no_image:
            error_string = error_string + "\n\n    Didn't get a Image \n\n"
        #create rectangle
        textRect = pygame.Rect((0, 0, screen_res[0], screen_res[1]))
        #set rectangle position to middle of the screen
        textRect.centerx = screen.get_rect().centerx
        textRect.centery = screen.get_rect().centery   
        #render the text for the rectangle
        rendered_text = render_textrect(error_string, basicFont, textRect, LGRAY, DGRAY, 0)
        if rendered_text:
            screen.blit(rendered_text, textRect)

    pygame.display.update()