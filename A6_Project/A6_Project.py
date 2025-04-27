# Assignment 6 by Yeji Kim (u1551284) and Hyunmin Kang (u1255204)
# Theme: Ghost Town
# Refactored version using class inheritance and new derived classes (PlatformEnemy, RotatingPowerUp)

import pygame, sys, random

# Pixel-perfect collision function
def pixel_collision(mask1, rect1, mask2, rect2):
    offset_x = rect2[0] - rect1[0]
    offset_y = rect2[1] - rect1[1]
    overlap = mask1.overlap(mask2, (offset_x, offset_y))
    return bool(overlap)

# Base Sprite class
class Sprite:
    def __init__(self, image):
        self.image = image
        self.rectangle = image.get_rect()
        self.mask = pygame.mask.from_surface(image)

    def draw(self, screen):
        screen.blit(self.image, self.rectangle)

    def is_colliding(self, other_sprite):
        return pixel_collision(self.mask, self.rectangle, other_sprite.mask, other_sprite.rectangle)

# Player class
class Player(Sprite):
    def set_position(self, new_position):
        self.rectangle.center = new_position

# Enemy class
class Enemy(Sprite):
    def __init__(self, image, width, height):
        super().__init__(image)
        self.rectangle = image.get_rect(center=(random.randint(0, width), random.randint(0, height)))
        self.speed = (random.choice([-3, -2, -1, 1, 2, 3]), random.choice([-3, -2, -1, 1, 2, 3]))

    def move(self):
        self.rectangle.move_ip(*self.speed)

    def bounce(self, width, height):
        vx, vy = self.speed
        if self.rectangle.left <= 0:
            vx = abs(vx)
            self.rectangle.left = 1
        elif self.rectangle.right >= width:
            vx = -abs(vx)
            self.rectangle.right = width - 1
        if self.rectangle.top <= 0:
            vy = abs(vy)
            self.rectangle.top = 1
        elif self.rectangle.bottom >= height:
            vy = -abs(vy)
            self.rectangle.bottom = height - 1
        self.speed = (vx, vy)

# PlatformEnemy class
class PlatformEnemy(Enemy):
    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        vx, vy = self.speed
        self.speed = (vx, 0)

# PowerUp class
class PowerUp(Sprite):
    def __init__(self, image, width, height):
        super().__init__(image)
        self.rectangle = image.get_rect(center=(random.randint(0, width), random.randint(0, height)))

# RotatingPowerUp class
class RotatingPowerUp(PowerUp):
    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        self.angle = 0
        self.original_image = image

    def draw(self, screen):
        self.angle += 3
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rectangle.center
        self.rectangle = self.image.get_rect()
        self.rectangle.center = old_center
        self.mask = pygame.mask.from_surface(self.image)
        super().draw(screen)

def main():
    pygame.init()
    myfont = pygame.font.SysFont('monospace', 24)
    width, height = 600, 400
    screen = pygame.display.set_mode((width, height))

    background_image = pygame.image.load("ghosty_background.png").convert()
    background_image = pygame.transform.smoothscale(background_image, (600, 400))
    ghosty_image = pygame.image.load("ghosty_player.png").convert_alpha()
    ghosty_image = pygame.transform.smoothscale(ghosty_image, (60, 60))
    spirit_image = pygame.image.load("ghosty_enemy.png").convert_alpha()
    spirit_image = pygame.transform.smoothscale(spirit_image, (50, 50))
    platform_image = pygame.image.load("ghosty_platform_enemy.png").convert_alpha()
    platform_image = pygame.transform.smoothscale(platform_image, (50, 50))
    orb_image = pygame.image.load("ghosty_orb.png").convert_alpha()
    orb_image = pygame.transform.smoothscale(orb_image, (40, 40))
    rotating_image = pygame.image.load("ghosty_rotating_orb.png").convert_alpha()
    rotating_image = pygame.transform.smoothscale(rotating_image, (40, 40))
    shield_image = pygame.image.load("ghosty_shield.png").convert_alpha()
    shield_image = pygame.transform.smoothscale(shield_image, (72, 72))
    shield_image.set_alpha(128)

    ghosty = Player(ghosty_image)
    spirits = [Enemy(spirit_image, width, height) for _ in range(3)] + [PlatformEnemy(platform_image, width, height) for _ in range(2)]
    orbs = []

    life = 3
    collected_orbs = 0
    shield_on = False
    recently_hit_spirits = set()
    is_playing = True

    while is_playing and life > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_playing = False

        ghosty.set_position(pygame.mouse.get_pos())

        for spirit in spirits:
            if ghosty.is_colliding(spirit):
                if shield_on:
                    shield_on = False
                    recently_hit_spirits.add(spirit)
                elif spirit not in recently_hit_spirits:
                    life -= 1.0
                    recently_hit_spirits.add(spirit)
            else:
                if spirit in recently_hit_spirits:
                    recently_hit_spirits.remove(spirit)

            spirit.move()
            spirit.bounce(width, height)

        for orb in orbs[:]:
            if ghosty.is_colliding(orb):
                life += 1
                collected_orbs += 1
                orbs.remove(orb)

        if collected_orbs >= 3:
            shield_on = True
            collected_orbs = 0

        screen.blit(background_image, (0, 0))
        ghosty.draw(screen)
        if shield_on:
            shield_rect = shield_image.get_rect(center=ghosty.rectangle.center)
            screen.blit(shield_image, shield_rect)

        for spirit in spirits:
            spirit.draw(screen)
        for orb in orbs:
            orb.draw(screen)

        if len(orbs) < 3 and random.randint(1, 100) <= 3:
            if random.random() < 0.5:
                orbs.append(PowerUp(orb_image, width, height))
            else:
                orbs.append(RotatingPowerUp(rotating_image, width, height))

        life_banner = myfont.render(f"Spirit Energy: {life:.1f}", True, (180, 140, 255))
        screen.blit(life_banner, (20, 20))

        pygame.display.update()
        pygame.time.wait(20)

    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
