import pygame
from .. import setup
from .. import tools
from  .. import constants as C
from .. components import info

class MainMenu:
    def __init__(self):
        game_info = {
            'score':0,#分数
            'coin':12,#金币
            'lives':3,#生命树
            'game_time':300,#游戏时间
            'player_state':'small',#角色初始状态
            'level':1#关卡
        }
        self.start(game_info)

    def start(self,game_info):
        self.game_info = game_info#上次死亡的游戏信息继承
        self.setup_background()#设置背景图
        self.setup_player()#设置玩家
        self.setup_cursor()#设置光标
        self.info = info.Info('main_menu',self.game_info)
        self.finished = False#模式选择状态
        self.next = 'load_screen'#下一个状态

    def setup_background(self):
        self.background = setup.GRAPHICS['level_1']#获取整个level1背景图
        self.background_rect = self.background.get_rect()#获得整个图片的矩形
        #放大图片矩形
        self.background = pygame.transform.scale(self.background,(int(self.background_rect.width*C.BG_MULTI),
                                                                    int(self.background_rect.height*C.BG_MULTI)))
        self.viewport = setup.SCREEN.get_rect()#游戏窗口滑动矩形
        self.caption = tools.get_image(setup.GRAPHICS['title_screen'],1,60,176,88,(255,0,220),C.BG_MULTI)#游戏标题





    def setup_player(self):#设置角色
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.PLAYER_MULTI)

    def setup_cursor(self):#设置光标
        self.cursor = pygame.sprite.Sprite()#光标继承精灵类
        #精灵cursor的图片
        self.cursor.image = tools.get_image(setup.GRAPHICS['item_objects'],24,160,8,8,(0,0,0),C.PLAYER_MULTI)
        #精灵cursor在哪里显示
        rect = self.cursor.image.get_rect()
        rect.x,rect.y = (220,360)
        self.cursor.rect = rect
        #cursor状态机
        self.cursor.state = '1P'

    def update_cursor(self,keys):#cursor状态更新
        if keys[pygame.K_UP]:#按下上方向键
            self.cursor.state = '1P'#状态选择1P
            self.cursor.rect.y = 360#1P状态下光标y坐标变为360
        elif keys[pygame.K_DOWN]:#按下方向键
            self.cursor.state = '2P'#状态2P
            self.cursor.rect.y = 405#光标y坐标变为405
        elif keys[pygame.K_RETURN]:#按下回车健（进入游戏）
            self.reset_game_info()#重置游戏信息
            if self.cursor.state == '1P':#选择1P模式进入游戏
                self.finished = True
            elif self.cursor.state == '2P':
                pass



    def update(self,surface,keys):#更新绘画
        #import random
        #surface.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        surface.blit(self.background,self.viewport)
        surface.blit(self.caption,(170,100))#把标题放在（170，100）坐标位置
        surface.blit(self.player_image,(110,490))
        surface.blit(self.cursor.image,self.cursor.rect)#更新显示精灵cursor

        self.info.update()#调用info的update
        self.update_cursor(keys)
        self.info.draw(surface)

    def reset_game_info(self):
        self.game_info.update({
            'score': 0,
            'coin': 0,
            'lives': 3,
            'player_state': 'small'
        })




