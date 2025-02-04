import pygame

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

run = True
while run:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

pygame.quit()