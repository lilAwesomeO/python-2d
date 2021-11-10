import pygame
from pygame.locals import *
import sys
import random 

#	Lag 2D gåing
#	Lag Map
#	Lag collision(Denne først)
# 	Lag hopping
#	Lag Portal-system?
#	Timed granater?

# inheritance fra sprites
class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__() 
		self.surf = pygame.Surface((30, 30))
		self.surf.fill((128,255,40))

		self.rect = self.surf.get_rect()
		
		self.pos = vec((10, 385))
		self.vel = vec(0,0)
		self.acc = vec(0,0)
	
	def move(self):
		self.acc = vec(0,0.5)
    
		pressed_keys = pygame.key.get_pressed()
                
		if pressed_keys[K_LEFT]:
			self.acc.x = -ACC
		if pressed_keys[K_RIGHT]:
			self.acc.x = ACC
                 
		self.acc.x += self.vel.x * FRIC
		self.vel += self.acc
		self.pos += self.vel + 0.5 * self.acc
         
		if self.pos.x > WIDTH:
			self.pos.x = 0
		if self.pos.x < 0:
			self.pos.x = WIDTH
             
		self.rect.midbottom = self.pos
	
	def update(self):
		hits = pygame.sprite.spritecollide(P1 , platforms, False)
		
		# hvis spilleren er på vei ned?
		if self.vel.y > 0:	
			if hits:
				self.pos.y = hits[0].rect.top + 1
				self.vel.y = 0
	
	def jump(self):
		hits = pygame.sprite.spritecollide(P1 , platforms, False)
		if hits:
		    self.vel.y = -15

class platform(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.surf = pygame.Surface((random.randint(50,100), 12))
		self.surf.fill((0,255,0))
		self.rect = self.surf.get_rect(center = (random.randint(0,WIDTH-10),random.randint(0, HEIGHT-30)))	

	def move(self):
		pass	

# what is get_rekt? you get a rect object which has surface-reference, size, and position
# what is it compared to surf? is just an area from the main surface of the screen. 
#  - create rects from it.
#  - 
# draw this engine

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
HEIGHT = 450
WIDTH = 400

ACC = 0.5
FRIC = -0.12
FPS = 60
 
 # Display 
FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Muh game")

# class
PT1 = platform()
PT1.surf = pygame.Surface((WIDTH, 20))
PT1.surf.fill((255,0,0))
PT1.rect = PT1.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

P1 = Player()

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

all_sprites.add(PT1)
all_sprites.add(P1)
platforms.add(PT1)


for x in range(random.randint(5, 6)):
    pl = platform()
    platforms.add(pl)
    all_sprites.add(pl)

while True:
	
	# now keys are processed in two functions :S
	for event in pygame.event.get():
		
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		
		if event.type == pygame.KEYDOWN:    
			if event.key == pygame.K_SPACE:
				P1.jump()

	displaysurface.fill((0,0,0))
	P1.update()

	for entity in all_sprites:
			displaysurface.blit(entity.surf, entity.rect)
			entity.move()
	
	pygame.display.update()
	FramePerSec.tick(FPS)
