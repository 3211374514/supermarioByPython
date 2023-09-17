#游戏入口
import pygame
from source import tools,setup,sound
from source.states import main_menu,load_screen,level
def main():

    #state状态字典
    state_dict ={
        'main_menu': main_menu.MainMenu(),
        'load_screen': load_screen.LoadScreen(),
        'level': level.Level(),
        'game_over': load_screen.GameOver()
    }
    game = tools.Game(state_dict, 'main_menu')
    #sound.music.play()
    game.run()


if __name__ == '__main__':
    main()