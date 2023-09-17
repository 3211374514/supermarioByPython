import pygame
from .. import tools,setup,sound
from .. import constants as C
from .. import constants2 as c
from .. components import powerup
import json
import os

class Player(pygame.sprite.Sprite):#精灵类
    def __init__(self,name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name#名字
        self.load_data()#载入玩家数据
        self.setup_states()#主角状态
        self.setup_velocities()#速度
        self.setup_timers()#计时器
        self.load_images()#图片帧

        # self.frame_index = 0
        # self.image = self.frames[self.frame_index]
        # self.rect = self.image.get_rect()

    def load_data(self):
        file_name = self.name + '.json'#P1或P2的JSON文件
        file_path = os.path.join('source/data/player',file_name)
        with open(file_path) as f:
            self.player_data = json.load(f)#载入玩家数据

    def setup_states(self):#主角状态指示
        self.state = 'stand'#设置初始状态
        self.face_right = True#脸的朝向
        self.dead = False#死亡状态
        self.big = False#变大状态
        self.fire = False#发射状态
        self.can_shoot = True#可以开火
        self.can_jump = True#允许跳跃
        self.hurt_immune = False#无敌状态
        self.in_castle = False

    def setup_velocities(self):#速度数值
        speed = self.player_data['speed']#从json文件中读取速度数据
        self.x_vel = 0#x方向上速度
        self.y_vel = 0#y方向上的速度

        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.jump_vel = speed['jump_velocity']
        self.walk_accel = speed['walk_accel']
        self.run_accel = speed['run_accel']
        self.turn_accel = speed['turn_accel']#转身时加速度
        self.gravity = C.GRAVITY#重力加速度
        self.anti_gravity = C.ANTI_GRAVITY#起跳重力加速度

        self.max_x_vel = self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel



    def setup_timers(self):#计时器
        self.walking_timer = 0#步行时长
        self.transition_timer = 0#变身时长
        self.death_timer = 0#死亡倒计时
        self.hurt_immune_timer = 0#无敌时间倒计时
        self.last_fireball_timer = 0#上一次发射火球的时间
        self.game_time = 0#
        self.flag_pole_right = 0


    def load_images(self):#主角帧造型加载
        sheet = setup.GRAPHICS['mario_bros']
        frame_rects = self.player_data['image_frames']

        self.right_small_normal_frames = []#you右小正常帧
        self.right_big_normal_frames = []#右大正常
        self.right_big_fire_frames = []#右大火球
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames,self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames,self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames,self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames
        ]
        #初始人物帧
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames


        for group,group_frame_rects in frame_rects.items():#将图片取出放到对应的帧库
            for frame_rect in group_frame_rects:
                right_image = tools.get_image(sheet,frame_rect['x'],frame_rect['y'],
                frame_rect['width'],frame_rect['height'],(0,0,0),C.PLAYER_MULTI)#得到一张图片
                left_image = pygame.transform.flip(right_image,True,False)
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)



        self.frame_index = 0#frame_index选择四张图片中的一张
        self.frames = self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()



    def update(self,keys,level):#人物帧
        self.currrent_time = pygame.time.get_ticks()#帧转换计时器
        self.handle_states(keys,level)#运动状态
        self.is_hurt_immune()#无敌时间判断



    def handle_states(self,keys,level):#运动状态控制
        self.can_jump_or_not(keys)
        self.can_shoot_or_not(keys)
        if self.state =='stand':
            self.stand(keys,level)
        elif self.state == 'walk':
            self.walk(keys,level)
        elif self.state == 'jump':
            self.jump(keys,level)
        elif self.state =='fall':
            self.fall(keys,level)
        elif self.state == 'die':
            self.die(keys)
        elif self.state == 'small2big':
            self.small2big(keys)
        elif self.state == 'big2small':
            self.big2small(keys)
        elif self.state == 'big2fire':
            self.big2fire(keys)
        elif self.state == 'flag_pole':
            self.flag_pole_sliding()


        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def can_jump_or_not(self,keys):#是否可以跳
        if not keys[pygame.K_a]:
            self.can_jump = True

    def can_shoot_or_not(self,keys):
        if not keys[pygame.K_s]:
            self.can_shoot = True

    def stand(self,keys,level):#站立状态机
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.state = 'walk'
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            self.state = 'walk'
        elif keys[pygame.K_a] and self.can_jump:#跳跃
            sound.small_jump.play(0)
            self.state = 'jump'
            self.y_vel = self.jump_vel
        elif keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def walk(self,keys,level):#走路状态机

        if keys[pygame.K_s]:#在walk中当s健被按下，切换到跑步，即最大速度和加速度切换到跑步的参数
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
            else:
                self.max_x_vel = self.max_run_vel
                self.x_accel = self.run_accel
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel


        if self.currrent_time - self.walking_timer >self.calc_frame_duration():#变化走路帧
            if self.frame_index < 3:
                self.frame_index +=1
            else:
                self.frame_index = 1
            self.walking_timer = self.currrent_time


        if keys[pygame.K_RIGHT]:
            self.face_right = True
            if self.x_vel < 0:#切换到加速跑
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,True)
        elif keys[pygame.K_LEFT]:#切换到急刹状态
            self.face_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,False)

        else:
            if self.face_right:
                self.x_vel -= self.x_accel#速度衰减
                if self.x_vel<0:#向右走速度是>0
                    self.x_vel = 0
                    self.state = 'stand'#切换到站立状态
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:#向左走速度是<0
                    self.x_vel = 0
                    self.state = 'stand'#切换到站立状态

        if keys[pygame.K_a] and self.can_jump:#跳跃
            sound.small_jump.play(0)
            self.state = 'jump'
            self.y_vel = self.jump_vel



    def jump(self,keys,level):
        self.frame_index = 4#切换jump动作帧
        #sound.big_jump.play(0)
        self.y_vel += self.anti_gravity
        self.can_jump = False

        if self.y_vel >= 0:#速度为0切换到下落
            self.state = 'fall'


        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.x_vel = self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,True)
        elif keys[pygame.K_LEFT]:#切换到急刹状态
            self.face_right = False
            self.x_vel = self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,False)
        if keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

        if not keys[pygame.K_a]:
            self.state = 'fall'


    def fall(self,keys,level):
        self.y_vel = self.calc_vel(self.y_vel,self.gravity,self.max_y_vel)
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.x_vel = self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,True)
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            self.x_vel = self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,False)
        elif keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def die(self,keys):
        self.rect.y += self.y_vel
        self.y_vel += self.anti_gravity

    def go_die(self):#主角死亡
        self.dead = True
        sound.main_theme_music.stop()
        sound.death_sound.play()
        self.y_vel = self.jump_vel
        self.frame_index = 6#死亡帧
        self.state = 'die'
        self.death_timer = self.currrent_time#记录死亡时间

    def small2big(self,keys):
        # sound.powerup.play(0)
        frame_dur = 65#变身切换时长
        sizes = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]
        frames_and_idx = [(self.small_normal_frames,0),(self.small_normal_frames,7),(self.big_normal_frames,0)]
        if self.transition_timer == 0:
            self.big = True
            self.transition_timer = self.currrent_time
            self.changing_idx = 0
        elif self.currrent_time - self.transition_timer >frame_dur:
            self.transition_timer = self.currrent_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames,idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def big2small(self,keys):
        frame_dur = 65  # 变身切换时长
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_idx = [(self.small_normal_frames, 0), (self.big_normal_frames, 0), (self.big_normal_frames, 4)]
        if self.transition_timer == 0:
            self.big = False
            self.transition_timer = self.currrent_time
            self.changing_idx = 0
        elif self.currrent_time - self.transition_timer > frame_dur:
            self.transition_timer = self.currrent_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def big2fire(self,keys):

        frame_dur = 65  # 变身切换时长
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_idx = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.transition_timer == 0:
            self.fire = True
            self.transition_timer = self.currrent_time
            self.changing_idx = 0
        elif self.currrent_time - self.transition_timer > frame_dur:
            self.transition_timer = self.currrent_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames



    def change_player_image(self,frames,idx):
        self.frame_index = idx
        if self.face_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx




    def calc_vel(self,vel,accel,max_vel,is_positive=True):#计算返回加速度
        if is_positive:
            return min(vel + accel,max_vel)
        else:
            return max(vel - accel,-max_vel)

    def calc_frame_duration(self):#计算摆臂频率
        duration = -30 / self.max_run_vel * abs(self.x_vel) + 100
        return duration

    def is_hurt_immune(self):#判断无敌时间
        if self.hurt_immune:
            if self.hurt_immune_timer == 0:
                self.hurt_immune_timer = self.currrent_time
                self.blank_image = pygame.Surface((1,1))#新建空白帧
            elif self.currrent_time - self.hurt_immune_timer < 2000:
                if (self.currrent_time - self.hurt_immune_timer) % 100 <50:#无敌时闪烁
                    self.image = self.blank_image
            else:
                self.hurt_immune = False
                self.hurt_immune_timer = 0

    def shoot_fireball(self,level):
        if self.currrent_time - self.last_fireball_timer > 300:
            sound.fireball_sound.play()
            self.frame_index = 6
            fireball = powerup.Fireball(self.rect.centerx,self.rect.centery,self.face_right)
            level.powerup_group.add(fireball)
            self.can_shoot = False
            self.last_fireball_timer = self.currrent_time

    def flag_pole_sliding(self):#从旗杆滑落
        """State where Mario is sliding down the flag pole"""

        print("flag_pole_sliding")
        self.frame_index = 10
        #self.state = c.FLAGPOLE
        #self.in_transition_state = True
        self.x_vel = 0
        self.y_vel = 0
        self.flag_pole_timer = 0

        if self.flag_pole_timer == 0:
            self.flag_pole_timer = self.currrent_time
        elif self.rect.bottom < 493:
            if (self.currrent_time - self.flag_pole_timer) < 65:
                self.image = self.right_frames[9]
            elif (self.currrent_time - self.flag_pole_timer) < 130:
                self.image = self.right_frames[10]
            elif (self.currrent_time - self.flag_pole_timer) >= 130:
                self.flag_pole_timer = self.currrent_time

            self.rect.right = self.flag_pole_right
            self.y_vel = 3
            self.rect.y += self.y_vel

            if self.rect.bottom >= 488:
                self.flag_pole_timer = self.currrent_time

        elif self.rect.bottom >= 493:
            self.image = self.right_frames[10]




