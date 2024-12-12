import pygame
from pygame.locals import *
import random
import os

#хранение результатов
folder_name = "FlappyBananaYeah"
file_name = "score.txt"
file_path = os.path.join(folder_name, file_name)
if not os.path.exists(file_path):
    with open(file_path, 'w') as file:
        file.write("Your result")


pygame.init()

#создание окна игры
clock = pygame.time.Clock()
fps = 90
screen_width = 564
screen_height = 636


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Banana')

#определение шрифта и цвета для игры
font = pygame.font.SysFont('Bauhas 93', 60)
white = (255, 255, 255)

#определение основных игровых переменных: скорость и т д
ground_scroll = 2
scroll_speed = 11
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = 1500 #миллисекунды
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

#загрузка основных изображений
bg = pygame.image.load('FlappyBananaYeah/icon/bg.png')
ground_img = pygame.image.load('FlappyBananaYeah/icon/ground.png')
button_img = pygame.image.load('FlappyBananaYeah/icon/restart.png')

#функция для рисовки текста
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#функция для сброса игры
def reset_game():
    global flying  
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flying = False  
    return 0  

#начальные параметры и изображение банана
class Banana(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'FlappyBananaYeah/icon/banana{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.space_pressed = False

    def update(self):
        global flying
        if flying == True:
        #гравитация
            self.vel += 0.5
        if self.vel > 8:
            self.vel = 8
        if self.rect.bottom < 568: 
            self.rect.y += int(self.vel)
        keys = pygame.key.get_pressed()
        if not game_over:
            #прыжок с мыши
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            #прыжок с пробела
            if keys[pygame.K_SPACE] and not self.space_pressed:
                self.space_pressed = True
                if not flying:
                    flying = True
                    self.vel = -10
                elif flying:
                    self.vel = -10
            #сброс при отпускании
            if not keys[pygame.K_SPACE]:
                self.space_pressed = False
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        #управление анимацией
        self.counter += 1
        flap_cooldown = 5
        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]
        #переворачиваем банан
            if self.vel > 0:
                self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
            else:
                self.image = pygame.transform.rotate(self.images[self.index], -90)

#основные параметры для создания труб 
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('FlappyBananaYeah/icon/pipe.png')
        self.rect = self.image.get_rect()
        #позиция 1, если сверху, то -1 - снизу
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
#функция для обновления состояния труб
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
#кнопка для перезапуска игры
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        #проверка, наведена ли мышь на кнопку
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        #кнопка рисования
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
banana_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Banana(100, int(screen_height / 2))
banana_group.add(flappy)
#создание экземпляра кнопки перезапуска
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)
#цикл игры
run = True 
while run:
    clock.tick(fps)
    #фон
    screen.blit(bg, (0,0))
    banana_group.draw(screen)
    banana_group.update()
    pipe_group.draw(screen)
    #земля
    screen.blit(ground_img, (ground_scroll, 568))
    #проверка результатов
    if len(pipe_group) > 0:
        if banana_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and banana_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if banana_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False 
    draw_text(str(score), font, white, int(screen_width / 2), 20)
    #поиск столкновений
    if pygame.sprite.groupcollide(banana_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    #проверка, есть ли на земле банан
    if flappy.rect.bottom >= 568:
        game_over = True
        flying = False
    if game_over == False and flying == True:
        #создание новых труб
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        #рисуем и прокручиваем землю
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 36:
            ground_scroll = 2

            pipe_group.update()
    #проверка, не закончилась ли игра, и выполнение сброса
    if game_over == True:
        if button.draw() == True:
            game_over = False
            with open(file_path, 'a') as file:
                file.write(f"Game score: {score}\n")
            score = reset_game()
    #события для окончания игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not flying and not game_over:
                flying = True
    #выход из библиотек и стирание файла для результатов
    pygame.display.update()
pygame.quit()
with open(file_path, 'w') as file:
    file.write("")

