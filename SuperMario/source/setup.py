import pygame
from . import constants as C
from . import tools


pygame.init()
SCREEN = pygame.display.set_mode((C.SCREEN_W,C.SCREEN_H))#新建屏幕
GRAPHICS = tools.load_graphics('resources/graphics')#加载图片
