import json
import os

import pygame
from .. components import info,brick,box,enemy,coin,flagpole,castle_flag
from .. import tools,setup,sound
from .. import constants as C
from .. import constants2 as c
from .. components import player,stuff

class Level:
    def start(self,game_info):
        self.game_info = game_info
        self.finished = False#该阶段完成状态
        self.next = 'game_over'
        self.info = info.Info('level',self.game_info)
        self.music = True
        self.load_map_data()  # 读取json文件map的数据
        self.setup_background()#建立背景
        self.setup_start_positions()  # 设置起始位置
        self.setup_player()#建立玩家
        self.setup_ground_items()#地面碰撞部件，水管，台阶等
        self.setup_bricks_and_boxes()#加载砖块he宝箱
        self.setup_enemies()#加载怪物
        self.setup_checkpoints()#检查点
        self.setup_fireball()#火球
        self.setup_music()#音乐
        self.setup_flag_pole()
        #sound.main_theme_music.play()




    def setup_flag_pole(self):
        """Creates the flag pole at the end of the level"""
        self.flag = flagpole.Flag(8505, 100)

        pole0 = flagpole.Pole(8505, 97)
        pole1 = flagpole.Pole(8505, 137)
        pole2 = flagpole.Pole(8505, 177)
        pole3 = flagpole.Pole(8505, 217)
        pole4 = flagpole.Pole(8505, 257)
        pole5 = flagpole.Pole(8505, 297)
        pole6 = flagpole.Pole(8505, 337)
        pole7 = flagpole.Pole(8505, 377)
        pole8 = flagpole.Pole(8505, 417)
        pole9 = flagpole.Pole(8505, 450)

        finial = flagpole.Finial(8507, 97)

        self.flag_pole_group = pygame.sprite.Group(self.flag,
                                               finial,
                                               pole0,
                                               pole1,
                                               pole2,
                                               pole3,
                                               pole4,
                                               pole5,
                                               pole6,
                                               pole7,
                                               pole8,
                                               pole9)


    def setup_music(self):
        if self.music:
            print("play music")
            sound.main_theme_music.play(-1)

    def setup_fireball(self):
        self.fireball_group = pygame.sprite.Group()
        pass



    def setup_checkpoints(self):#加载检查点
        self.checkpoint_group = pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x, y, w, h = item['x'], item['y'], item['width'], item['height']
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x,y,w,h,checkpoint_type,enemy_groupid))



    def setup_enemies(self):#加载也怪
        self.dying_group = pygame.sprite.Group()
        self.shell_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_group_dict = {}#野怪字典
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id,enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group



    def setup_bricks_and_boxes(self):#得到砖块数据
        self.brick_group = pygame.sprite.Group()#创建砖块精灵组
        self.box_group = pygame.sprite.Group()#创建宝箱组
        self.coin_group = pygame.sprite.Group()#金币组
        self.powerup_group = pygame.sprite.Group()#道具组

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x,y = brick_data['x'],brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:
                    if 'brick_num' in brick_data:
                        # TODO 批量处理
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x,y,brick_type,None))
                elif brick_type == 1:
                    #sound.coin.play(0)
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.coin_group))
                else:
                    #sound.powerup_appears.play(0)
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.powerup_group))



        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x,y = box_data['x'],box_data['y']
                box_type = box_data['type']

                if box_type == 1:
                    self.box_group.add(box.Box(x,y,box_type,self.coin_group))
                else:
                    self.box_group.add(box.Box(x,y,box_type,self.powerup_group))


    def setup_ground_items(self):#得到地图部件
        self.ground_items_group = pygame.sprite.Group()#把所有部件放入一个精灵族
        for name in ['ground','pipe','step']:
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'],item['y'],item['width'],item['height'],name))


    def load_map_data(self):#读取map的json数据
        if self.game_info['level'] == 1:
            file_name = 'level_1.json'#关卡
        elif self.game_info['level'] == 2:
            file_name = 'level_2.json'
        file_path = os.path.join('source/data/maps',file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_start_positions(self):#从json读取起始位置信息
        self.positions = []
        for data in self.map_data['maps']:
            self.positions.append((data['start_x'],data['end_x'],data['player_x'],data['player_y']))
        self.start_x,self.end_x,self.player_x,self.player_y = self.positions[0]

    def setup_player(self):#玩家初始化
        self.player = player.Player('mario')
        self.player.rect.x = self.game_window.x + self.player_x#player_x指角色相对窗口的位置
        self.player.rect.bottom = self.player_y#player_u指角色脚的位置

    def setup_background(self):
        self.image_name = self.map_data['image_name']#获取level.json中的地图背景数据
        self.background = setup.GRAPHICS[self.image_name]
        rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background,(int(rect.width*C.BG_MULTI),
                                                                  int(rect.height*C.BG_MULTI)))
        self.background_rect = self.background.get_rect()
        self.game_window = setup.SCREEN.get_rect()#游戏滑动窗口
        self.game_ground = pygame.Surface((self.background_rect.width,self.background_rect.height))#创建空白背景




    def update(self,surface,keys):
        self.current_time = pygame.time.get_ticks()
        self.player.update(keys,self)#传入按键操作



        if self.player.dead:#主角死亡
            if self.current_time - self.player.death_timer >3000:#如果进入死亡3s
                self.finished = True

                self.update_game_info()#更新游戏信息
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()  # 更新玩家位置
            self.check_checkpoints()#检查点方法
            #self.check_points_check()
            self.check_if_go_die()  #检查是否死亡
            self.update_game_window()
            self.info.update()
            self.brick_group.update()#跟新砖块
            self.box_group.update()#更新宝箱
            self.enemy_group.update(self)#更新野怪
            self.dying_group.update(self)#更新死亡野怪
            self.shell_group.update(self)#更新龟壳
            self.coin_group.update(self)#更新金币
            self.powerup_group.update(self)#更新道具
            self.update_game_time()
            self.flag_pole_group.update()







        self.draw(surface)

    def update_game_time(self):
        self.current_time = pygame.time.get_ticks()
        if self.current_time - self.player.game_time > 1000:
            #print("game_time")
            self.game_info['game_time'] -= 1
            self.player.game_time = self.current_time
            if self.game_info['game_time'] < 0:
                sound.out_of_time_sound.play()
                self.player.go_die()

    def is_frozen(self):
        #print("is_frozen")
        return self.player.state in ['small2big','big2small','big2fire','fire2small','flag pole']

    def update_player_position(self):#更新玩家位置
        self.player.rect.x += self.player.x_vel#新位置=原位置+速度
        if self.player.rect.x < self.start_x:#不能走回头路
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:#不能超过地图末尾
            self.player.rect.right = self.end_x
        self.check_x_collisions()#检测x上的碰撞

        if not self.player.dead:#如果主角死亡不需要进入y轴验证
            self.player.rect.y += self.player.y_vel
            self.check_y_collisions()#检测y上的碰撞

    def check_x_collisions(self):#x方向的碰撞
        check_group = pygame.sprite.Group(self.ground_items_group,self.brick_group,self.box_group)
        #检查一个精灵 是否 与精灵组里任意一个精灵有碰撞,返回第一个与角色碰撞的精灵
        collided_sprite = pygame.sprite.spritecollideany(self.player,check_group)
        if collided_sprite:#发生碰撞，调整角色位置
            self.adjust_player_x(collided_sprite)

        if self.player.hurt_immune:
            return
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy :
            if self.player.big:
                self.player.state = 'big2small'
                self.player.hurt_immune = True
            else:
                self.player.go_die()
                pass
        #龟壳
        shell = pygame.sprite.spritecollideany(self.player,self.shell_group)
        if shell:
            if shell.state == 'slide':
                self.player.go_die()
            else:
                sound.kick.play()
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 10
                    shell.rect.x += 40
                    shell.direction = 1
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 40
                    shell.direction = 0
                shell.state = 'slide'
        #道具
        powerup = pygame.sprite.spritecollideany(self.player,self.powerup_group)
        coin = pygame.sprite.spritecollideany(self.player,self.coin_group)
        if powerup:#吃到道具
            if powerup.name == 'fireball':
                pass
            elif powerup.name == 'mushroom':
                powerup.kill()
                sound.powerup.play(0)
                self.player.state = 'small2big'
            elif powerup.name == 'fireflower':
                powerup.kill()
                if self.player.big:
                    sound.powerup.play(0)
                    self.player.state = 'big2fire'
                else:
                    self.player.state = 'small2big'
        if coin:#吃到金币
            if coin.name == 'coin':
                print("coin")
                coin.kill()
                self.game_info['coin'] += 1
                self.game_info['score'] += 100

    def check_y_collisions(self):#y方向的碰撞
        group_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)#与地图组件碰撞，台阶水管
        brick = pygame.sprite.spritecollideany(self.player,self.brick_group)#与砖块碰撞
        box = pygame.sprite.spritecollideany(self.player,self.box_group)#与宝箱碰撞
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        # if collided_sprite:  # 发生碰撞，调整角色位置
        #     self.adjust_player_y(collided_sprite)
        #self.check_will_fall(self.player)

        if brick and box:
            to_brick = abs(self.player.rect.centerx - brick.rect.centerx)
            to_box = abs(self.player.rect.centerx - box.rect.centerx)
            if to_brick > to_box:
                brick = None
            else:
                box = None


        if group_item:
            self.adjust_player_y(group_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        #踩到敌人
        elif enemy:
            if self.player.hurt_immune:
                return
            self.enemy_group.remove(enemy)#移出活野怪组
            if enemy.name =='koopa':#如果踩死的是乌龟
                self.shell_group.add(enemy)
            else:
                self.dying_group.add(enemy)#加入死亡组
            if self.player.y_vel <0:#如果碰撞时角色处于上升状态
                how = 'bumped'#顶飞
            else:
                how = 'trampled'#踩扁
                sound.kick.play()
                self.player.state = 'jump'
                self.player.rect.bottom = enemy.rect.top
                self.player.y_vel = self.player.jump_vel * 0.9
            enemy.go_die(how,1 if self.player.face_right else -1)
        self.check_will_fall(self.player)
            #pass

    def adjust_player_x(self,sprite):
        if self.player.rect.x <sprite.rect.x:
            self.player.rect.right = sprite.rect.left#相当于向右走碰到台阶被挡住
        else:
            self.player.rect.left = sprite.rect.right#相当于向左走碰到台阶被挡住
        self.player.x_vel = 0#速度变为零

    def adjust_player_y(self,sprite):
        #下落碰撞
        if self.player.rect.bottom < sprite.rect.bottom:#角色的脚底小于碰撞面
            self.player.y_vel = 0#下落加速度归零
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'#状态切换为walk
        #跳跃碰撞
        else:
            self.player.y_vel = 7#碰撞后反弹加速度
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'#状态改为下落fall

            self.is_enemy_on(sprite)#检测砖块上是否有怪物

            if sprite.name == 'box':
                if sprite.state == 'rest':
                    sprite.go_bumped()
            if sprite.name == 'brick':
                if self.player.big and sprite.brick_type ==0:
                    sprite.smashed(self.dying_group)
                else:
                    sprite.go_bumped()

    def is_enemy_on(self,sprite):#判断砖块上有怪物
        sprite.rect.y -= 1
        enemy = pygame.sprite.spritecollideany(sprite,self.enemy_group)
        if enemy:#怪物死亡
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if sprite.rect.centerx > enemy.rect.centerx:
                enemy.go_die('bumped',-1)
            else:
                enemy.go_die('bumped',1)
        sprite.rect.y += 1



    def check_will_fall(self,sprite):#检查是否应该下落
        sprite.rect.y += 1#将该精灵下落1个位置
        check_group = pygame.sprite.Group(self.ground_items_group,self.brick_group,self.box_group)
        collided_sprite = pygame.sprite.spritecollideany(sprite,check_group)#检查下落1后是否会发生碰撞
        if not collided_sprite and sprite.state != 'jump' and not self.is_frozen():#判断不会发生碰撞且角色不处于jump
            sprite.state = 'fall'#状态改为fall开始下落
        sprite.rect.y -= 1#最后角色复位




    def update_game_window(self):#实现窗口滑动
        third = self.game_window.x + self.game_window.width * 2 /3#计算屏幕三分之二位置
        if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x:#当角色速度不为0且位置大于2/3
            self.game_window.x += self.player.x_vel#更新屏幕画面
            self.start_x = self.game_window.x#随着游戏窗口实时更新start_x


    def draw(self,surface):
        self.game_ground.blit(self.background,self.game_window,self.game_window)#绘制背景到game_ground
        self.game_ground.blit(self.player.image,self.player.rect)#绘制人物到game_ground
        self.powerup_group.draw(self.game_ground)#绘制道具
        self.brick_group.draw(self.game_ground)#绘画砖块
        self.box_group.draw(self.game_ground)#绘画宝箱
        #绘画每组怪物
        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)#龟壳
        #绘画道具
        self.coin_group.draw(self.game_ground)
        self.flag_pole_group.draw(self.game_ground)

        surface.blit(self.game_ground,(0,0),self.game_window)#把game_ground画到屏幕
        self.info.draw(surface)

    def check_if_go_die(self):
        if self.player.rect.y > C.SCREEN_H: #马里奥掉出屏幕外
            self.player.go_die()

    def update_game_info(self):
        if self.player.dead:
            self.game_info['game_time'] = 300
            self.game_info['lives'] -= 1
        if self.game_info['lives'] == 0:
            self.next = 'game_over'
        else:
            self.next = 'load_screen'


    def check_checkpoints(self):

        checkpoint = pygame.sprite.spritecollideany(self.player,self.checkpoint_group)
        if(checkpoint):
            if checkpoint.checkpoint_type == 0:#野怪
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            elif checkpoint.checkpoint_type == 1:#旗杆
                print("pole_flag")
                sound.flagpole_music.play(0)
                #self.player.invincible = False
                self.player.state = 'flag_pole'
                self.player.flag_pole_right = checkpoint.rect.right
                if self.player.rect.bottom < self.flag.rect.y:
                    self.player.rect.bottom = self.flag.rect.y
                self.flag.state = c.SLIDE_DOWN
                self.create_flag_points()
            elif checkpoint.checkpoint_type == 2:#城堡
                print("checkpoint_type == '2'")
                sound.stage_clear_music.play(0)
                self.state = c.IN_CASTLE
                self.player.kill()
                self.player.state == 'stand'
                self.player.in_castle = True
                #castle_flag.Flag.update(self)
                self.flag_pole_group.add(castle_flag.Flag(8750, 322))
                #self.game_info['level'] += 1
                sound.main_theme_music.stop()
                self.timer = pygame.time.get_ticks()
                if self.current_time - self.timer > 3000:

                    self.finished = True
                    self.next = 'load_screen'
                #self.overhead_info_display.state = c.FAST_COUNT_DOWN
            checkpoint.kill()

    def create_flag_points(self):

        x = 8518
        y = c.GROUND_HEIGHT - 60
        mario_bottom = self.player.rect.bottom

        if mario_bottom > (c.GROUND_HEIGHT - 40 - 40):

            self.game_info['score'] +=100
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 160):

            self.game_info['score'] += 400
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 240):

            self.game_info['score'] += 800
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 360):

            self.game_info['score'] += 2000
        else:

            self.game_info['score'] += 5000







