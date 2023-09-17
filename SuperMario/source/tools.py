#工具及游戏主控
import sys
import  os
import pygame
import random
#pygame.init()
class Game:
    def __init__(self,state_dict,start_state):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()#时钟
        self.keys = pygame.key.get_pressed()
        self.state_dict = state_dict#状态字典
        self.state = self.state_dict[start_state]

    def update(self):#状态切换update
        if self.state.finished:#如果finied状态为True即按下回车
            game_info = self.state.game_info#保存本次的游戏信息
            next_state = self.state.next
            self.state.finished = False
            self.state = self.state_dict[next_state]
            self.state.start(game_info)#将游戏信息传入下一阶段
        self.state.update(self.screen,self.keys)



    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                    #sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()

            self.update()
            pygame.display.update()
            self.clock.tick(60)#刷新率每秒60帧

def load_graphics(path,accept=('.jpg','.png','.bmp','.gif')):
    graphics = {}
    for pic in os.listdir(path):
        name,ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path,pic))
            if img.get_alpha():
                img = img.convert_alpha()#如果图片有alpha透明图层转化
            else:
                img = img.convert()
            graphics[name] = img
    return graphics

def get_image(sheet,x,y,width,height,colorkey,scale):#从素材图裁剪得到所需图像
    image = pygame.Surface((width,height))
    image.blit(sheet,(0,0),(x,y,width,height))#原图，左上角x，左上角y，宽，高，图片裁剪底色
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image,(int(width*scale),int(height*scale)))
    return image

def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', 'jpg', 'bmp')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics



