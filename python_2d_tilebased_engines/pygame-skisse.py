# Pygame template - skeleton for a new pygame project
import sys
import pygame

from pygame.locals import *
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
#=========================================#
# kilde på lru_cache og ThreadPoolExecutor: 
# 	¤ https://towardsdatascience.com/3-easy-and-noninvasive-ways-to-instantly-boost-your-python-code-performance-b21cd823f37e
#
###################################################################################################
#																  #
# 	[NB]~* THIS DOES NOT CHECK FOR OUT OF BOUNDS! *~[NB]							  #
#		I think its okay, nothing has happened to me when i wander of the map and back again, #
#		but know that no limits to the characters position have been set in this code.	  #
#																  #
###################################################################################################

# *~Magic numbers of pristine and salient wizardry~*
WIDTH = 512
HEIGHT = 512
FPS = 60

SPRITESHEET_LOCATION = "./assets/rpgsheet.png"
MAP_LOCATION = "./map2.txt"
TEXTURE_COORDS = TABLE = TILES = SCREEN = MAP = RUN = False
LAYER3_TILES = "tsTSdDcC^*"


# rendering/general
def quit():
	pygame.quit()
	sys.exit()


# map loading
def create_sprites(map):
	tiles=[]
	for y, line in enumerate(map):
		for x, c in enumerate(line.strip()):
			# hvis tilen indikerer et tré, "legg" først "gress" under det
			if c in LAYER3_TILES:
				tiles.append(Tile(TEXTURE_COORDS['-'],x*32,y*32))			
			tiles.append(Tile(TEXTURE_COORDS[c],x*32,y*32))
	return set(tiles)


# map loading
def loadMap(url):
	mapped = []
	lineIndex = 0
	with open(url) as f:
		for line in f:
			mapped.append(line)
	return mapped


# map loading
def load_tile_table(filename, width, height):
	image = pygame.image.load(filename).convert_alpha()
	image_width, image_height = image.get_size()
	
	tile_table = []

	for tile_x in range(0, image_width//width):
		line = []
		tile_table.append(line)
		
		for tile_y in range(0, image_height//height):
			rect = (tile_x*width, tile_y*height, width, height)
			line.append(image.subsurface(rect))	
	return tile_table


# map loading
class Tile(pygame.sprite.Sprite):
	def __init__(self, image, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()		
		
		self.rect.x = x
		self.rect.y = y

		self.to_draw = True;
	
	def update(self):
		self.to_draw = False
	
#class Player(pygame.sprite.Sprite):
class Player(Tile):
	
	def __init__(self, dir_images,x,y):
		super().__init__(dir_images[0],x,y)
		self.rect.center = (WIDTH / 2, HEIGHT / 2)
		self.dir_images = dir_images

	def set_img(self, dir):
		self.image = self.dir_images[dir]

	# 0 down, 1 left, 2 up, 3 right
	# ha en dict hvor "d" betyr "down," dr" betyr "down right" og referer til 
	# korresponderende bilder	
	
	# boolean istedet? en pressed key gjør en bolean true, en released setter den false?

	# controls(but also rendering due to set_img)
	def move(self):
		pressed_keys = pygame.key.get_pressed()
		
		if pressed_keys[K_LEFT] or pressed_keys[ord('a')]:
			self.rect.x = self.rect.x - 1
			self.set_img(1)

		if pressed_keys[K_RIGHT] or pressed_keys[ord('d')]:
			self.rect.x = self.rect.x + 1
			self.set_img(2)

		if pressed_keys[K_UP] or pressed_keys[ord('w')]:
			self.rect.y = self.rect.y - 1
			self.set_img(3)

		if pressed_keys[K_DOWN] or pressed_keys[ord('s')]:
			self.rect.y = self.rect.y + 1
			self.set_img(0)

		if pressed_keys[ord('q')]:
			quit()

	def update(self):
		for t in set(pygame.sprite.spritecollide(self, TILES, False)):
			t.to_draw = True			


# rendering/general
def process_tile(t):
	t.update()
	return SCREEN.blit(t.image,t.rect)


# rendering/general
pygame.init()
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
pygame.display.set_caption("WOLOLOOooooo")

FLAGS = DOUBLEBUF # | FULLSCREEN
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT),FLAGS,8)

# map loading
TABLE = load_tile_table(SPRITESHEET_LOCATION, 32, 32)
TEXTURE_COORDS={'-' : TABLE[14][1], 's' : TABLE[8][2],'*' : TABLE[11][9],'^' : TABLE[12][9], 't' : TABLE[9][1]}
MAP = loadMap(MAP_LOCATION)
TILES = pygame.sprite.Group()
player = Player([TABLE[7][12],TABLE[7][13],TABLE[7][14],TABLE[7][15]], (WIDTH//2) - 32, (HEIGHT//2) - 32)
TILES.add(create_sprites(MAP))
TILES.add(player)

DRAWN_RECTS = []
clock = pygame.time.Clock()


# av en eller anen grunn er while(1): raskere enn "while True:"
#	 kilde på det: https://www.codeproject.com/Articles/5298051/Improving-Performance-in-Pygame-Speed-Up-Your-Game
# men tydeligvis ikke i python 3?
while(1):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()

#=====================#
#	Random 2do notes:
#=====================#
#
#	hard collision. vi kan detecte om spilleren går over en tile knirkefritt, men vi må også ha pure collision.
#	enten så må tiles bety hva som skal på skjermen vs hva som er i "spillverdenen"
#	ha en y og x loop
#	så ha en default texture(f.eks gress) som kan endres bitwise(til interior/sand/vann)
# 	bruk en bitwise operasjon for å sjekke om det er noe *annet* enn default texture
#	re-render alt når mappen scroller, men bare berørte tiles/objekter som flytter på seg hvis ikke
# 	kanskje dict maps; en tile kan ha en eller flere vals
# 	vær additional val kan representere et additional layer
# 	begyn med 3 layers, player kan være 2
#=========================================================================================#

	# prøver å bare redraw tiles som er berørt(for å forhindre tearing; 
	# i.e. at bevegende sprites "henger igjen")
	#for entity in set([potential for potential in set(TILES) if potential.to_draw]):
		
		# disabler neste drawing(ved hjelp av en linje som lagrer retkangler 
		#	returnert av vinduets "blitte"(drawe) funksjon)
	#	entity.to_draw = not TO_UPDATE.append(SCREEN.blit(entity.image, entity.rect))
	
	player.move()
	clock.tick(FPS)
	with ThreadPoolExecutor(max_workers=4) as executor:
		# burde jeg kjøre set selv for TILES her?
		# big boss line incoming
		DRAWN_RECTS = list(executor.map(lambda t: process_tile(t), [potential for potential in TILES if potential.to_draw]))
		#==================#
		# dette betyr altså:
		#==================#
		#
		#	kjør "process_tile(t)"" på de tiles som har booleanen "to_draw" satt til "True."
		#	"process_tile" tegner tilen, og returnerer dimensjonene/lokasjonene til 'tegningen i form av "DRAWN_RECTS".
		#	"to_draw" vil bli satt automatisk til false under spillets oppdateringsfunksjon
		#	og vil bare settes til "True" igjen når en spiller går over tilens surface area.
		#
		#	"DRAWN_RECTS", som altså er lokasjon/dimensjon for kun tiles spilleren har interacted med,
		#	sendes så til spillets oppdateringsfunksjon, og bare dem blir oppdatert.
		#	Spilleren sin sprite blir også redrawet, fordi spillerens "to_draw" er alltid satt til "True." 
		#	På den måten kan vi få bedre performance ut av en pygame-engine.
	pygame.display.update(DRAWN_RECTS)
pygame.quit()