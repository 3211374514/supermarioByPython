import pygame
from .. import setup,tools,sound
from ..components import box
from .. import constants as C


def create_enemy(enemy_data):
    enemy_type = enemy_data['type']
    x, y_bottom,direction,color = enemy_data['x'],enemy_data['y'],enemy_data['direction'],enemy_data['color']


    if enemy_type ==0:#Goomba 蘑菇怪
        enemy = Goomba(x, y_bottom,direction,"goomba",color)
    elif enemy_type == 1:
        enemy = Koopa(x, y_bottom,direction,"koopa",color)

    return enemy

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y_bottom,direction,name,frame_rects):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.name = name
        self.frame_index = 0
        self.left_frames = []
        self.right_frames = []

        self.load_frames(frame_rects)
        self.frames = self.left_frames if self.direction == 0 else self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y_bottom

        self.timer = 0
        self.x_vel = -1 * C.ENEMY_SPEED if self.direction == 0 else C.ENEMY_SPEED
        self.y_vel = 0
        self.gravity = C.GRAVITY
        self.state = 'walk'

    def load_frames(self,frame_rects):
        for frame_rect in frame_rects:
            left_frame = tools.get_image(setup.GRAPHICS['enemies'],*frame_rect,(0,0,0),C.ENEMY_MULTI)
            right_frame = pygame.transform.flip(left_frame,True,False)
            self.left_frames.append(left_frame)
            self.right_frames.append(right_frame)

    def update(self,level):  # 人物帧
        self.current_time = pygame.time.get_ticks()  # 帧转换计时器
        self.handle_states(level)  # 运动状态
        self.uptate_position(level)

    def handle_states(self,level):  # 运动状态控制


        if self.state == 'walk':
            self.walk()

        elif self.state == 'fall':
            self.fall()
        elif self.state == 'die':
            self.die()
        elif self.state == 'trampled':
            self.trampled(level)
        elif self.state =='slide':
            self.slide()

        if self.direction:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def walk(self):
        if self.current_time - self.timer > 125:
            self.frame_index = (self.frame_index + 1)%2
            self.image = self.frames[self.frame_index]
            self.timer = self.current_time

    def fall(self):
        if self.y_vel <10:
            self.y_vel += self.gravity

    def die(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if (self.rect.y) > C.SCREEN_H:
            self.kill()

    def trampled(self,level):#踩死

        self.x_vel = 0
        self.frame_index = 2
        if self.death_timer == 0:
            self.death_timer = self.current_time
        if self.current_time - self.death_timer > 500:
            self.kill()

    def slide(self):
        pass


    def uptate_position(self,level):
        self.rect.x += self.x_vel
        self.check_x_collision(level)
        self.rect.y += self.y_vel
        if self.state != 'die':
            self.check_y_collision(level)

    def check_x_collision(self,level):
        sprite = pygame.sprite.spritecollideany(self,level.ground_items_group)
        powerup_sprite = pygame.sprite.spritecollideany(self,level.powerup_group)
        if sprite:
            if self.direction:
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1
        if powerup_sprite:#被火球打死
            if powerup_sprite.name == 'fireball':
                powerup_sprite.frame_index = 4
                powerup_sprite.state = 'boom'
                self.go_die(how = 'bumped',direction= 1 if level.player.face_right else -1)
                level.enemy_group.remove(self)
                level.dying_group.add(self)

        if self.state =='slide':
            enemy = pygame.sprite.spritecollideany(self,level.enemy_group)
            if enemy:
                sound.kick.play()
                enemy.go_die(how = 'slide',direction=self.direction)
                level.enemy_group.remove(enemy)
                level.dying_group.add(enemy)

    def check_y_collision(self,level):
        check_group = pygame.sprite.Group(level.ground_items_group,level.box_group,level.brick_group)
        sprite = pygame.sprite.spritecollideany(self,check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'
        level.check_will_fall(self)

    def go_die(self,how,direction=1):
        self.death_timer = self.current_time
        if how in ['bumped','slide']:#顶飞
            self.x_vel = C.ENEMY_SPEED * direction
            self.y_vel = -8
            self.gravity = 0.6
            self.state = 'die'
            self.frame_index = 2
        elif how == 'trampled':#踩死
            self.state = 'trampled'



class Koopa(Enemy):
    def __init__(self,x, y_bottom,direction,name,color):
        bright_rect_frames = [(96, 9, 16, 22), (112, 9, 16, 22),(160,9,16,22)]
        dark_rect_frames = [(96,72,16,22),(112,72,16,22),(160,72,16,22)]

        if not color:
            frame_rects = bright_rect_frames
        else:
            frame_rects = dark_rect_frames

        Enemy.__init__(self,x, y_bottom,direction,name,frame_rects)
        self.shell_timer = 0
    def trampled(self,level):
        self.x_vel = 0
        self.frame_index = 2


        if self.shell_timer ==0:
            self.shell_timer = self.current_time
        if self.current_time - self.shell_timer >5000:
            self.state = 'walk'
            self.x_vel = -C.ENEMY_SPEED if self.direction ==0 else C.ENEMY_SPEED
            level.enemy_group.add(self)
            level.shell_group.remove(self)
            self.shell_timer = 0



class Goomba(Enemy):
    def __init__(self, x, y, direction, name, color):
        bright_rect_frames = [(0,16,16,16),(16,16,16,16),(32,16,16,16)]
        dark_rect_frames = [(0,48,16,16),(16,48,16,16),(32,48,16,16)]

        if not color:
            frame_rects = bright_rect_frames
        else:
            frame_rects = dark_rect_frames

        Enemy.__init__(self, x, y, direction, name, frame_rects)











