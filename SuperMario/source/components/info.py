import pygame
from .. import constants as C
from . import coin
from .. import setup,tools

pygame.font.init()

class Info:
    def __init__(self,state,game_info):
        self.state = state
        self.game_info = game_info
        self.create_state_labels()#创造某个阶段特有的文字
        self.create_info_labels()#创建通用文字
        self.flash_coin = coin.FlashingCoin(game_info)

    def create_state_labels(self):
        self.state_labels = []
        if self.state == 'main_menu':#主菜单的文字，内容和坐标位置
            self.state_labels.append((self.create_label('1  PLAYER  GAME'),(272,360)))
            self.state_labels.append((self.create_label('2  PLAYER  GAME'), (272, 405)))
            self.state_labels.append((self.create_label('TOP - '), (290, 465)))
            self.state_labels.append((self.create_label('000000'), (400, 465)))
        elif self.state == 'load_screen':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1 - 1'), (430, 200)))
            self.state_labels.append((self.create_label('X   {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.BG_MULTI)
        elif self.state == 'game_over':
            self.state_labels.append((self.create_label('GAME OVER'), (280, 300)))

    def create_info_labels(self):
        self.info_labels = []
        self.info_labels.append((self.create_label('MARIO'), (75, 30)))
        self.info_labels.append((self.create_label('COIN'), (275, 30)))
        self.info_labels.append((self.create_label('WORLD'), (450, 30)))
        self.info_labels.append((self.create_label('TIME'), (625, 30)))
        self.info_labels.append((self.create_label('{}'.format(self.game_info['game_time'])), (640, 55)))
        self.info_labels.append((self.create_label('{}'.format(self.game_info['score'])), (75, 55)))
        self.info_labels.append((self.create_label('x{}'.format(self.game_info['coin'])), (300, 55)))
        self.info_labels.append((self.create_label('1 - 1'), (480, 55)))




    def create_label(self,label,size=40,width_scale=1.25,height_scale=1):#生成文字
        font = pygame.font.SysFont(C.FONT, size)#设置字体和字号
        label_image = font.render(label,0,(255,255,255))#字体生成图片
        #通过缩小文字图片再放大得到低像素文字风格
        rect = label_image.get_rect()
        label_image = pygame.transform.scale(label_image,(int(rect.width*width_scale),
                                                          int(rect.height*height_scale)))
        return label_image




    def update(self):#更新
        self.flash_coin.update()
        #self.info_labels.append((self.create_label('x{}'.format(self.game_info['coin'])), (300, 55)))
        self.create_info_labels()

    def draw(self,surface):#绘画
        #surface.blit(self.create_label('HELLO WORD',size=60),(100,400))
        for label in self.state_labels:
            surface.blit(label[0],label[1])
        for label in self.info_labels:
            surface.blit(label[0],label[1])
        surface.blit(self.flash_coin.image,self.flash_coin.rect)

        if self.state == 'load_screen':
            surface.blit(self.player_image,(300,270))





