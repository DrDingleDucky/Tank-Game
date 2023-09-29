import math
import os
import random
import sys
import time

import pygame

import levels

pygame.init()

WIN_WIDTH = 1200
WIN_HEIGHT = 816
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("Tanks")
pygame.display.set_icon(pygame.image.load(os.path.join("icon", "icon.png")).convert_alpha())
pygame.mouse.set_visible(False)

# player colour
BLUE = (0, 0, 255)

# tank colours
LIGHT_BROWN = (122, 76, 42)
GREEN = (0, 128, 0)
YELLOW = (245, 187, 39)
PURPLE = (255, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# explosion colours
ORANGE = (255, 128, 0)
LIGHT_GRAY = (128, 128, 128)

# background colours
WHITE_1 = (255, 255, 255)
WHITE_2 = (247, 247, 247)
GRAY_1 = (32, 32, 32)
GRAY_2 = (40, 40, 40)

player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()
player_bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
collision_tile_group = pygame.sprite.Group()
backgound_tile_group = pygame.sprite.Group()
partical_list = []

FONT_1 = pygame.font.Font(os.path.join("font", "comic_sans.ttf"), 42)

pygame.mixer.set_num_channels(128)
load_level_sound = pygame.mixer.Sound(os.path.join("sounds", "load_level.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join("sounds", "explosion.wav"))
shoot_sound_1 = pygame.mixer.Sound(os.path.join("sounds", "shoot_1.wav"))
shoot_sound_2 = pygame.mixer.Sound(os.path.join("sounds", "shoot_2.wav"))
shoot_sound_3 = pygame.mixer.Sound(os.path.join("sounds", "shoot_3.wav"))
shoot_sound_list = [shoot_sound_1, shoot_sound_2, shoot_sound_3]
bounce_sound_1 = pygame.mixer.Sound(os.path.join("sounds", "bounce_1.wav"))
bounce_sound_2 = pygame.mixer.Sound(os.path.join("sounds", "bounce_2.wav"))
bounce_sound_3 = pygame.mixer.Sound(os.path.join("sounds", "bounce_3.wav"))
bounce_sound_list = [bounce_sound_1, bounce_sound_2, bounce_sound_3]
bullet_explosion_sound_1 = pygame.mixer.Sound(os.path.join("sounds", "bullet_explosion_1.wav"))
bullet_explosion_sound_2 = pygame.mixer.Sound(os.path.join("sounds", "bullet_explosion_2.wav"))
bullet_explosion_sound_3 = pygame.mixer.Sound(os.path.join("sounds", "bullet_explosion_3.wav"))
bullet_explosion_list = [bullet_explosion_sound_1, bullet_explosion_sound_2, bullet_explosion_sound_3]


class Player(pygame.sprite.Sprite):
    def __init__(self, colour, size, speed, shoot_delay, bullet_colour, bullet_speed,
                 bullet_max_bounces, bullet_size, pos_x, pos_y):
        super().__init__()
        self.colour = colour
        self.speed = speed
        self.shoot_delay = shoot_delay
        self.bullet_colour = bullet_colour
        self.bullet_speed = bullet_speed
        self.bullet_max_bounces = bullet_max_bounces
        self.bullet_size = bullet_size
        self.width = size
        self.height = size
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(colour)
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))
        self.direction = pygame.math.Vector2(0, 0)
        self.rect_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.shoot_timer = self.shoot_delay

    def horizontal_movement(self, delta_time):
        if pygame.key.get_pressed()[pygame.K_a]:
            self.direction.x = -1
        elif pygame.key.get_pressed()[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        self.rect_pos.x += self.direction.x * self.speed * delta_time
        self.rect.x = round(self.rect_pos.x)

    def horizontal_collisions(self):
        for sprite in collision_tile_group.sprites():
            if sprite.rect.colliderect(self):
                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left
                    self.rect_pos.x = sprite.rect.left - self.width
                elif self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                    self.rect_pos.x = sprite.rect.right

    def vertical_movement(self, delta_time):
        if pygame.key.get_pressed()[pygame.K_w]:
            self.direction.y = -1
        elif pygame.key.get_pressed()[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        self.rect_pos.y += self.direction.y * self.speed * delta_time
        self.rect.y = round(self.rect_pos.y)

    def vertical_collisions(self):
        for sprite in collision_tile_group.sprites():
            if sprite.rect.colliderect(self):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.rect_pos.y = sprite.rect.top - self.height
                elif self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.rect_pos.y = sprite.rect.bottom

    def shoot(self, delta_time):
        if pygame.mouse.get_pressed()[0]:
            if self.shoot_timer < 0:
                random.choice(shoot_sound_list).play()
                player_bullet_group.add(Bullet(
                    self.bullet_colour,
                    self.bullet_speed,
                    self.bullet_max_bounces,
                    self.bullet_size,
                    player_group.sprite.rect.center,
                    pygame.mouse.get_pos()))
                self.shoot_timer = self.shoot_delay

        self.shoot_timer -= delta_time

    def update(self, delta_time):
        self.horizontal_movement(delta_time)
        self.horizontal_collisions()
        self.vertical_movement(delta_time)
        self.vertical_collisions()
        self.shoot(delta_time)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, colour, size, speed, shoot_delay, bullet_colour, bullet_speed,
                 bullet_max_bounces, bullet_size, pos_x, pos_y):
        super().__init__()
        self.colour = colour
        self.speed = speed
        self.shoot_delay = shoot_delay
        self.bullet_colour = bullet_colour
        self.bullet_speed = bullet_speed
        self.bullet_max_bounces = bullet_max_bounces
        self.bullet_size = bullet_size
        self.width = size
        self.height = size
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(colour)
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))
        self.direction = pygame.math.Vector2(0, 0)
        self.rect_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.shoot_timer = random.randint(1, 20) / 10
        self.direction_change_timer = random.randint(2, 5)
        self.direction_list = [-1, 1]
        self.direction.x = random.choice(self.direction_list)
        self.direction.y = random.choice(self.direction_list)

    def horizontal_movement(self, delta_time):
        self.rect_pos.x += self.direction.x * self.speed * delta_time
        self.rect.x = round(self.rect_pos.x)

    def horizontal_collisions(self):
        for sprite in collision_tile_group.sprites():
            if sprite.rect.colliderect(self):
                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left
                    self.rect_pos.x = sprite.rect.left - self.width
                    self.direction.x *= -1
                elif self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                    self.rect_pos.x = sprite.rect.right
                    self.direction.x *= -1

    def vertical_movement(self, delta_time):
        self.rect_pos.y += self.direction.y * self.speed * delta_time
        self.rect.y = round(self.rect_pos.y)

    def vertical_collisions(self):
        for sprite in collision_tile_group.sprites():
            if sprite.rect.colliderect(self):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.rect_pos.y = sprite.rect.top - self.height
                    self.direction.y *= -1
                elif self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.rect_pos.y = sprite.rect.bottom
                    self.direction.y *= -1

    def direction_change(self, delta_time):
        self.direction_change_timer -= delta_time
        if self.direction_change_timer < 0:
            self.direction.x = random.choice(self.direction_list)
            self.direction.y = random.choice(self.direction_list)
            self.direction_change_timer = random.randint(2, 5)

    def shoot(self, delta_time):
        self.shoot_timer -= delta_time
        if self.shoot_timer < 0:
            random.choice(shoot_sound_list).play()
            for sprite in player_group.sprites():
                enemy_bullet_group.add(Bullet(self.bullet_colour, self.bullet_speed, self.bullet_max_bounces, self.bullet_size, self.rect.center,
                                              (sprite.rect.center[0] + random.randint(-100, 100), sprite.rect.center[1] + random.randint(-100, 100))))
            self.shoot_timer = self.shoot_delay

    def update(self, delta_time):
        self.horizontal_movement(delta_time)
        self.horizontal_collisions()
        self.vertical_movement(delta_time)
        self.vertical_collisions()
        self.direction_change(delta_time)
        self.shoot(delta_time)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_colour, bullet_speed, bullet_max_bounces, bullet_size, start_pos, target_pos):
        super().__init__()
        self.bullet_colour = bullet_colour
        self.bullet_speed = bullet_speed
        self.max_bounces = bullet_max_bounces
        self.width = bullet_size
        self.height = bullet_size
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(center=start_pos)
        center_x, center_y = self.rect.center
        target_x, target_y = target_pos
        self.rise = target_y - center_y
        self.run = target_x - center_x
        self.angle = math.atan2(self.rise, self.run)
        self.delta_y = math.sin(self.angle) * self.bullet_speed
        self.delta_x = math.cos(self.angle) * self.bullet_speed
        self.rect_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.bounce_index = 0

    def movement(self, delta_time):
        self.rect_pos.x += self.delta_x * delta_time
        self.rect_pos.y += self.delta_y * delta_time
        self.rect.x = round(self.rect_pos.x)
        self.rect.y = round(self.rect_pos.y)

    def collisions(self):
        for sprite in collision_tile_group.sprites():
            if self.rect.colliderect(sprite):
                left = abs(self.rect.right - sprite.rect.left)
                right = abs(self.rect.left - sprite.rect.right)
                top = abs(self.rect.bottom - sprite.rect.top)
                bottom = abs(self.rect.top - sprite.rect.bottom)

                if (left < right and left < top and left < bottom and
                        self.delta_x > 0):
                    self.delta_x *= -1
                    self.bounce_index += 1
                elif (right < left and right < top and right < bottom and self.delta_x < 0):
                    self.delta_x *= -1
                    self.bounce_index += 1
                elif (top < left and top < right and top < bottom and self.delta_y > 0):
                    self.delta_y *= -1
                    self.bounce_index += 1
                elif (bottom < left and bottom < right and bottom < top and self.delta_y < 0):
                    self.delta_y *= -1
                    self.bounce_index += 1

    def bounce_bullet(self):
        for sprite in collision_tile_group.sprites():
            if self.rect.colliderect(sprite) and self.bounce_index <= self.max_bounces:
                random.choice(bounce_sound_list).play()

                for _ in range(50):
                    partical_list.append(Partical(LIGHT_GRAY, random.randint(self.width / 2, self.width * 2), random.randint(90, 180),
                                                  random.randint(-180, 180), random.randint(-180, 180), (self.rect.x + self.width / 2 + random.randint(-4, 4)),
                                                  (self.rect.y + self.height / 2 + random.randint(-4, 4))))

    def explode_bullet(self):
        if self.bounce_index > self.max_bounces:
            random.choice(bullet_explosion_list).play()
            Bullet.kill(self)

            for _ in range(50):
                partical_list.append(Partical(ORANGE, random.randint(self.width, self.width * 2), random.randint(60, 120), random.randint(-250, 250),
                                              random.randint(-250, 250), (self.rect.x + self.width / 2 + random.randint(-4, 4)),
                                              (self.rect.y + self.height / 2 + random.randint(-4, 4))))

    def draw(self):
        partical_list.append(Partical(self.bullet_colour, self.width / 1.8, random.randint(25, 65), random.randint(-30, 30),
                                      random.randint(-30, 30), self.rect_pos.x + self.width / 2 + random.randint(-4, 4),
                                      self.rect_pos.y + self.height / 2 + random.randint(-4, 4)))

    def update(self, delta_time):
        self.movement(delta_time)
        self.collisions()
        self.bounce_bullet()
        self.explode_bullet()


class Tile(pygame.sprite.Sprite):
    def __init__(self, colour_list, pos_x, pos_y):
        super().__init__()
        self.width = 48
        self.height = self.width
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(random.choice(colour_list))
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))


class Partical():
    def __init__(self, colour, radius, srink_speed, x_vel, y_vel, x_pos, y_pos):
        self.colour = colour
        self.radius = radius
        self.srink_speed = srink_speed
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.x_pos = x_pos
        self.y_pos = y_pos

    def move(self, delta_time):
        self.x_pos += self.x_vel * delta_time
        self.y_pos += self.y_vel * delta_time

    def scale(self, delta_time):
        self.radius -= self.srink_speed * delta_time

    def remove(self):
        if self.radius < 0:
            partical_list.remove(self)

    def draw(self):
        pygame.draw.circle(WIN, self.colour, (self.x_pos, self.y_pos), self.radius)

    def update(self, delta_time):
        self.move(delta_time)
        self.scale(delta_time)
        self.remove()


class Game():
    def __init__(self):
        self.current_level = 0
        self.game_active = False
        self.white_colour_list = [WHITE_1, WHITE_2]
        self.gray_colour_list = [GRAY_1, GRAY_2]
        self.start_text = FONT_1.render("Press Space To Start", True, BLACK)
        self.start_text_rect = self.start_text.get_rect(center=(WIN_WIDTH / 2, 0))
        self.level_text = FONT_1.render(f"Level Menu", True, BLACK)
        self.level_text_rect = self.level_text.get_rect(center=(WIN_WIDTH / 2, 24))

    def level_setup(self, level_data):
        for collom_index, row in enumerate(level_data):
            for row_index, char in enumerate(row):
                x = row_index * 48
                y = collom_index * 48

                if char == " ":
                    tile = Tile(self.white_colour_list, x, y)
                    backgound_tile_group.add(tile)
                elif char == "T":
                    tile = Tile(self.gray_colour_list, x, y)
                    collision_tile_group.add(tile)
                elif char == "U":
                    player = Player(BLUE, 48, 120, 0.25, BLUE, 260, 1, 16, x, y)
                    player_group.add(player)
                elif char == "L":
                    enemy = Enemy(LIGHT_BROWN, 48, 0, 1.8, LIGHT_BROWN, 260, 1, 16, x, y)
                    enemy_group.add(enemy)
                elif char == "G":
                    enemy = Enemy(GREEN, 48, 120, 1, GREEN, 260, 1, 16, x, y)
                    enemy_group.add(enemy)
                elif char == "Y":
                    enemy = Enemy(YELLOW, 48, 120, 1, YELLOW, 520, 0, 16, x, y)
                    enemy_group.add(enemy)
                elif char == "P":
                    enemy = Enemy(PURPLE, 48, 60, 0.25, PURPLE, 260, 1, 16, x, y)
                    enemy_group.add(enemy)
                elif char == "R":
                    enemy = Enemy(RED, 48, 0, 0.8, RED, 780, 3, 16, x, y)
                    enemy_group.add(enemy)
                elif char == "W":
                    enemy = Enemy(WHITE_1, 48, 240, 0.35, WHITE_1, 780, 1, 16, x, y)
                    enemy_group.add(enemy)

    def level_clear(self):
        player_group.empty()
        enemy_group.empty()
        player_bullet_group.empty()
        enemy_bullet_group.empty()
        collision_tile_group.empty()
        backgound_tile_group.empty()

    def level_update(self):
        if not self.game_active:
            if len(player_group) == 0:
                self.level_setup(levels.level_menu)
                load_level_sound.play()
        elif len(enemy_group) == 0:
            self.level_clear()
            self.current_level += 1
            load_level_sound.play()

            if self.current_level == 1:
                self.level_setup(levels.level_10)
            elif self.current_level == 2:
                self.level_setup(levels.level_2)
            elif self.current_level == 3:
                self.level_setup(levels.level_3)
            elif self.current_level == 4:
                self.level_setup(levels.level_4)
            elif self.current_level == 5:
                self.level_setup(levels.level_5)
            elif self.current_level == 6:
                self.level_setup(levels.level_6)
            elif self.current_level == 7:
                self.level_setup(levels.level_7)
            elif self.current_level == 8:
                self.level_setup(levels.level_8)
            elif self.current_level == 9:
                self.level_setup(levels.level_9)
            elif self.current_level == 10:
                self.level_setup(levels.level_10)
            elif self.current_level == 11:
                self.level_setup(levels.level_sucessfull)
                self.game_active = False
        elif len(player_group) == 0:
            self.level_clear()
            self.game_active = False

    def player_bullet_bullet_collisions(self):
        for index_1, sprite_1 in enumerate(player_bullet_group.sprites()):
            for index_2, sprite_2 in enumerate(player_bullet_group.sprites()):
                if sprite_1.rect.colliderect(sprite_2.rect) and index_1 != index_2:
                    random.choice(bullet_explosion_list).play()
                    sprite_1.kill()
                    sprite_2.kill()

                    for _ in range(50):
                        partical_list.append(Partical(ORANGE, random.randint(round(sprite_1.width / 2), round(sprite_1.width * 2)), random.randint(90, 180),
                                                      random.randint(-180, 180), random.randint(-180, 180), (sprite_1.rect.x + sprite_1.width / 2 + random.randint(-4, 4)),
                                                      (sprite_1.rect.y + sprite_1.height / 2 + random.randint(-4, 4))))

                    for _ in range(50):
                        partical_list.append(Partical(ORANGE, random.randint(round(sprite_2.width / 2), round(sprite_2.width * 2)),
                                                      random.randint(90, 180), random.randint(-180, 180), random.randint(-180, 180),
                                                      (sprite_2.rect.x + sprite_2.width / 2 + random.randint(-4, 4)), (sprite_2.rect.y + sprite_2.height / 2 + random.randint(-4, 4))))
                    return

    def player_enemy_bullet_collision(self):
        for sprite_1 in player_bullet_group.sprites():
            for sprite_2 in enemy_bullet_group.sprites():
                if sprite_1.rect.colliderect(sprite_2.rect):
                    random.choice(bullet_explosion_list).play()
                    sprite_1.kill()
                    sprite_2.kill()

                    for _ in range(50):
                        partical_list.append(Partical(ORANGE, random.randint(round(sprite_1.width / 2), round(sprite_1.width * 2)), random.randint(90, 180),
                                                      random.randint(-180, 180), random.randint(-180, 180), (sprite_1.rect.x + sprite_1.width / 2 + random.randint(-4, 4)),
                                                      (sprite_1.rect.y + sprite_1.height / 2 + random.randint(-4, 4))))

                    for _ in range(50):
                        partical_list.append(Partical(ORANGE, random.randint(round(sprite_2.width / 2), round(sprite_2.width * 2)), random.randint(90, 180),
                                                      random.randint(-180, 180), random.randint(-180, 180), (sprite_2.rect.x + sprite_2.width / 2 + random.randint(-4, 4)),
                                                      (sprite_2.rect.y + sprite_2.height / 2 + random.randint(-4, 4))))

    def bullet_enemy_collision(self):
        for sprite_1 in player_bullet_group.sprites():
            for sprite_2 in enemy_group.sprites():
                if sprite_1.rect.colliderect(sprite_2):
                    explosion_sound.play()
                    sprite_1.kill()
                    sprite_2.kill()

                    for _ in range(50):
                        partical_list.append(Partical(ORANGE, random.randint(sprite_1.width, sprite_1.width * 2), random.randint(40, 90),
                                                      random.randint(-500, 500), random.randint(-500, 500), (sprite_1.rect.x + sprite_1.width / 2 + random.randint(-4, 4)),
                                                      (sprite_1.rect.y + sprite_1.height / 2 + random.randint(-4, 4))))

    def bullet_player_collision(self):
        for sprite_1 in enemy_bullet_group.sprites():
            for sprite_2 in player_group.sprites():
                if sprite_1.rect.colliderect(sprite_2):
                    explosion_sound.play()
                    sprite_1.kill()
                    sprite_2.kill()

                    for _ in range(50):
                        partical_list.append(Partical(ORANGE, random.randint(sprite_1.width, sprite_1.width * 2), random.randint(40, 90),
                                                      random.randint(-500, 500), random.randint(-500, 500), (sprite_1.rect.x + sprite_1.width / 2 + random.randint(-4, 4)),
                                                      (sprite_1.rect.y + sprite_1.height / 2 + random.randint(-4, 4))))

    def pointer_update(self):
        for sprite in player_group.sprites():
            self.center_x, self.center_y = sprite.rect.center
            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            self.rise = self.mouse_y - self.center_y
            self.run = self.mouse_x - self.center_x
            self.angle = math.atan2(self.rise, self.run)
            self.delta_y = math.sin(self.angle)
            self.delta_x = math.cos(self.angle)

    def pointer_draw(self):
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 8, self.mouse_y + self.delta_y - self.rise / 8), 8)
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 4, self.mouse_y + self.delta_y - self.rise / 4), 8)
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 2.66, self.mouse_y + self.delta_y - self.rise / 2.66), 8)
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 2, self.mouse_y + self.delta_y - self.rise / 2), 8)
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 1.62, self.mouse_y + self.delta_y - self.rise / 1.62), 8)
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 1.36, self.mouse_y + self.delta_y - self.rise / 1.36), 8)
        pygame.draw.circle(WIN, BLUE, (self.mouse_x + self.delta_x - self.run / 1.16, self.mouse_y + self.delta_y - self.rise / 1.16), 8)
        pygame.draw.circle(WIN, BLUE, pygame.mouse.get_pos(), 8)

    def text_update(self):
        if self.game_active:
            self.level_text = FONT_1.render(f"Level {self.current_level}", True, BLACK)
        elif not self.game_active and self.current_level == 11:
            self.level_text = FONT_1.render(f"Level Sucessfull", True, BLACK)
        elif not self.game_active:
            self.level_text = FONT_1.render(f"Level Menu", True, BLACK)

        self.level_text_rect = self.level_text.get_rect(center=(WIN_WIDTH / 2, 24))

        if not self.game_active:
            self.start_text_rect.y = round(math.sin(time.time() * 2.5) * 50 + 616)

    def text_draw(self):
        WIN.blit(self.level_text, self.level_text_rect)

        if not self.game_active:
            WIN.blit(self.start_text, self.start_text_rect)

    def update(self, delta_time):
        self.level_update()

        player_group.update(delta_time)
        enemy_group.update(delta_time)
        player_bullet_group.update(delta_time)
        enemy_bullet_group.update(delta_time)

        for partical in partical_list:
            partical.update(delta_time)

        self.player_bullet_bullet_collisions()
        self.player_enemy_bullet_collision()
        self.bullet_enemy_collision()
        self.bullet_player_collision()

        self.pointer_update()

        self.text_update()

    def draw(self):
        WIN.fill(WHITE_1)
        collision_tile_group.draw(WIN)
        backgound_tile_group.draw(WIN)
        player_group.draw(WIN)
        enemy_group.draw(WIN)

        for sprite in player_bullet_group.sprites():
            sprite.draw()

        for sprite in enemy_bullet_group.sprites():
            sprite.draw()

        for partical in partical_list:
            partical.draw()

        self.pointer_draw()

        self.text_draw()
        pygame.display.update()


def main():
    previous_time = time.time()
    game = Game()

    while True:
        delta_time = time.time() - previous_time
        previous_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    if not game.game_active:
                        game.level_clear()
                        partical_list.clear()
                        game.current_level = 0
                        game.game_active = True

        game.update(delta_time)
        game.draw()


if __name__ == "__main__":
    main()
