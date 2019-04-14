import os
import random
import sys

import pygame
from pygame.locals import *


SCREENRECT = Rect(0, 0, 640, 480)


def load_image(filename):
    path = os.path.join(
        os.path.abspath(os.path.join("assets", os.pardir)),
        "assets",
        filename
    )

    try:
        surface = pygame.image.load(path)
    except pygame.error:
        raise SystemExit('Could not load image "{}" {}'.format(path, pygame.get_error()))

    return surface.convert()


class Snake(pygame.sprite.Sprite):
    speed = 1

    def __init__(self, head=None, row=0, x=None, y=None):
        super(Snake, self).__init__(self.containers)
        self.image = load_image("green_box.gif")
        self.size_x, self.size_y = self.image.get_size()
        self.head = head
        self.row = row

        if not x and not y:
            self.rect = self.image.get_rect(center=SCREENRECT.center)
        else:
            self.rect = self.image.get_rect(left=x, top=y)

        self.direction = "UP"

    def __repr__(self):
        return "Snake({})".format(self.row)

    def update(self):
        y = 0
        x = 0

        if self.head and self.head.old_direction:
            self.old_direction = self.direction
            self.direction = self.head.old_direction

        direction = {
            "DOWN": self.speed * self.size_x,
            "UP": -1 * self.speed * self.size_x,
            "RIGHT": self.speed * self.size_y,
            "LEFT": -1 * self.speed * self.size_y
        }[self.direction]

        if self.direction == "UP" or self.direction == "DOWN":
            y = direction
        else:
            x = direction

        if self.rect.x > SCREENRECT.width:
            self.rect.x = SCREENRECT.width - self.rect.x
        elif self.rect.x < 0:
            self.rect.x = SCREENRECT.width + self.rect.x

        if self.rect.y > SCREENRECT.height:
            self.rect.y = SCREENRECT.height - self.rect.y
        elif self.rect.y < 0:
            self.rect.y = SCREENRECT.height + self.rect.y

        self.rect.move_ip(x, y)


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Food, self).__init__(self.containers)
        self.image = load_image("red_box.jpg")
        self.rect = self.image.get_rect(left=SCREENRECT.width - x, top=SCREENRECT.height - y)


def grow_snake(snakes):
    head = snakes.sprites()[-1]

    y = head.rect.top
    x = head.rect.left

    if head.direction == "UP":
        y = y + head.size_y
    elif head.direction == "DOWN":
        y = y - head.size_y
    elif head.direction == "LEFT":
        x = x + head.size_x
    elif head.direction == "RIGHT":
        x = x - head.size_x

    snakes.add(Snake(head, len(snakes.sprites()), x, y))


def add_food(foods, snakes):
    x = random.randint(0, SCREENRECT.width)
    y = random.randint(0, SCREENRECT.height)

    food = Food(x, y)

    if pygame.sprite.spritecollideany(food, snakes):
        return add_food(foods, snakes)

    foods.add(food)


def play():
    pygame.init()

    winstyle = 0
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    pygame.display.set_caption('Snake')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(SCREENRECT.size)
    screen.blit(background, (0,0))
    pygame.display.flip()

    snakes = pygame.sprite.OrderedUpdates()
    foods = pygame.sprite.RenderUpdates()
    Snake.containers = snakes
    Food.containers = foods

    head = Snake()
    snakes.add(head)
    grow_snake(snakes)

    clock = pygame.time.Clock()

    add_food(foods, snakes)

    while head.alive():
        for event in pygame.event.get():
            if event.type == QUIT:
                return

            pygame.display.flip()

        keystate = pygame.key.get_pressed()

        head.old_direction = head.direction
        if head.direction == "UP" or head.direction == "DOWN":
            direction = keystate[K_LEFT] - keystate[K_RIGHT]
            if direction == 1:
                head.direction = "LEFT"
            elif direction == -1:
                head.direction = "RIGHT"
        else:
            direction = keystate[K_UP] - keystate[K_DOWN]
            if direction == 1:
                head.direction = "UP"
            elif direction == -1:
                head.direction = "DOWN"

        snakes.clear(screen, background)
        snakes.update()

        for coll in pygame.sprite.spritecollide(head, foods, True):
            grow_snake(snakes)
            add_food(foods, snakes)

        for coll in pygame.sprite.spritecollide(head, snakes, False):
            if coll == head:
                continue

            head.kill()

        foods.clear(screen, background)
        foods.update()

        dirty_snakes = snakes.draw(screen)
        pygame.display.update(dirty_snakes)

        dirty_foods = foods.draw(screen)
        pygame.display.update(dirty_foods)

        clock.tick(10)


if __name__ == "__main__":
    play()
