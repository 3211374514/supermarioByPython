import pygame
from .. components import info
from .. import sound


class LoadScreen:#载入界面
    def start(self,game_info):
        self.game_info = game_info
        self.finished = False
        self.next = 'level'#下一个状态
        self.duration = 2000#持续时间
        self.timer = 0#状态切换计时器
        self.info = info.Info('load_screen',self.game_info)#load页面文字

    def update(self,surface,keys):
        self.draw(surface)
        if self.timer ==0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > self.duration:#load_screen暂停界面2s
            self.finished = True
            self.timer = 0

    def draw(self,surface):
        surface.fill((0,0,0))
        self.info.draw(surface)

class GameOver(LoadScreen):
    def start(self,game_info):
        sound.game_over_sound.play()
        self.game_info = game_info
        self.finished = False
        self.next = 'main_menu'
        self.duration = 5000
        self.timer = 0
        self.info = info.Info('game_over',self.game_info)





