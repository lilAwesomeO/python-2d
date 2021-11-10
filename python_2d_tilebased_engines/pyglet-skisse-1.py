import pyglet
from pyglet.window import key, mouse

#=======#
#~TO DO~:
#=====#=#========================================================================================#
	#
	# ¤ Simple features:
	#	- animasjoner
	#	- Camera-tracking, 
	#	- større maps som ikke er viewport-bound,
	#	- flere bevegelige sprites uten å gå sub 60 fps, 
	#	- splitte av tile/player-klassene til sine egne filer/mapper
	#	- layering av tiles under runtime(trær på gress osv) uten å lagre noe ekstra på disk
	#
	# ¤ Increase performance(cython? enklere/mer low-level tile/sprite-constructs?)
	# ¤ Så lag en ryddigere object/component orientert versjon
	# ¤ Mer avanserte features? threading? online?
	#
	#==========================================================================================#

TILESIZE = 32
MOTION_CONSTANT=48

#foreløpig både viewport og map-bounds
WIDTH=512
HEIGHT=512

# anti aliasing på, 3d depth buffer av, stencil size er drawing relatert iirc og ikke viktig for sprites
config = pyglet.gl.Config(sample_buffers=1,samples=2, double_buffer=True, depth_size=0, stencil_size=0)
WINDOW = pyglet.window.Window(width=WIDTH,height=HEIGHT,resizable=True,caption='my gnarly knights',vsync=True)

pyglet.resource.path = ['./assets']
SPRITESHEET = pyglet.resource.image('rpgsheet.png')
SPRITESHEET2 = pyglet.resource.image('brahladin.png')
main_batch = pyglet.graphics.Batch()
keys = key.KeyStateHandler()
WINDOW.push_handlers(key)


def prepare_map_line(line): 
	return map(lambda c: MAP_ENCODING[c], line.strip())


def prepare_map(filepath):
	with open(filepath) as f:
		return map(lambda l: prepare_map_line(l), f.readlines())


def get_tile(image,x,y, group): 
	return Tile(image,x,y, group)

# skal i fremtiden ikke ha egne arrays av sprites for collidable sprites, men dette er en placeholder for now.
def make_collide(): 
	COLLIDABLE = []
	for y, line in enumerate(prepare_map("./collide.txt")):
		for x, c in enumerate(line):
			if c == "2":
				COLLIDABLE.append(get_tile(TREE1, x*TILESIZE, y*TILESIZE, MID_SPRITES))

	return COLLIDABLE


def create_tiles():
	tiles = []

	for y, t in enumerate(MAP):
		row = []
		for x, c in enumerate(t):
			tiles.append(get_tile(TEXTURES[int(c)],x*TILESIZE,y*TILESIZE,GROUND_SPRITES))

	return tiles

def update(dt):
	for obj in set(TILES): 
		obj.update(dt)


class Tile(pyglet.sprite.Sprite):
	def __init__(self,image,x,y, group):
		pyglet.sprite.Sprite.__init__(self,image,x,y,batch=main_batch,group=group)
		#self.to_draw = True
		self.x = x
		self.y = y
	def update(self, dt):
		pass
		#self.batch = None
		#self.to_draw = True
	

class Player(Tile):
	def __init__(self, image,x, y):
		self.keys = dict(left=False, right=False, up=False, down=False)
		super(Player, self).__init__(image, x, y,group=MID_SPRITES)
		#self.to_draw = True
		self.x = x
		self.y = y
		self.velocity_x, self.velocity_y  = 0.0, 0.0

	def check (self,n,n2):
		return n + TILESIZE > n2 and n < n2 + TILESIZE

	def check_pos(self, tile):
		return self.check(self.x, tile.x) and self.check(self.y, tile.y)

	def move(self, to_moveX, to_moveY):		
		"""
		Denne linjen er 'stygg' men jeg forsøker å increase performance

		hvis en foreslåtte posisjon(to_moveX, to_moveY) er utenfor HEIGHT/WIDTH grensen(viewporten for now), 
		eller hvis de foreslåtte posisjonene kolliderer med collidables; 
		ikke adopter de foreslåtte posisjonene,
		"""
		if to_moveX > WIDTH - TILESIZE or to_moveX < 0 or to_moveY > HEIGHT - TILESIZE or to_moveY < 0 or [c for c in set(COLLIDABLE) if self.check(to_moveX, c.x) and self.check(to_moveY, c.y)]:
			return False

		self.x = to_moveX
		self.y = to_moveY
		

		# eksperimenterer med selektiv oppdatering bare for tiles som har blitt interacted med, slik som pygame-skissen min
		#for t in set(TILES):
		#	if self.check_pos(t):
		#		t.batch = main_batch

	def update(self,dt):
		to_moveX = to_moveY = 0

		if self.keys["up"]: to_moveY = (dt * MOTION_CONSTANT)
		if self.keys["down"]: to_moveY = -(dt * MOTION_CONSTANT)
		if self.keys["left"]: to_moveX = -(dt * MOTION_CONSTANT)	
		if self.keys["right"]: to_moveX = (dt * MOTION_CONSTANT)
		
		if to_moveX or to_moveY:
			self.move(self.x + to_moveX, self.y + to_moveY)
			
##################
# ~*~TEXTURES~*~ #
##################
GRASS1 = SPRITESHEET.get_region(x=(14 * TILESIZE),y=(14* TILESIZE),width=TILESIZE,height=TILESIZE)
SAND1 = SPRITESHEET.get_region(x=(11 * TILESIZE),y=(11* TILESIZE),width=TILESIZE,height=TILESIZE)
TREE1 =SPRITESHEET.get_region(x=(8 * TILESIZE),y=(13 * TILESIZE),width=TILESIZE,height=TILESIZE)
PLAYER1 = SPRITESHEET2.get_region(x=(0 * TILESIZE),y=(0 * TILESIZE),width=TILESIZE,height=TILESIZE)
TEXTURES = [GRASS1,SAND1,TREE1,PLAYER1]
	
###############
# ~*~TILES~*~ #
###############
MAP_ENCODING={"#":"0","s":"2"}
MAP = prepare_map("./map1.txt")


################
# ~*~GROUPS~*~ #
################
GROUND_SPRITES = pyglet.graphics.OrderedGroup(0)
MID_SPRITES = pyglet.graphics.OrderedGroup(1)
TREE_SPRITES = pyglet.graphics.OrderedGroup(2)

TILES = create_tiles()
PLAYER = Player(PLAYER1,WIDTH //2,HEIGHT //2)
COLLIDABLE = make_collide()

CLOCK = pyglet.clock
dt = CLOCK.tick()

# bør ideelt sett ikke selektivt schedule en oppdatering for player her
CLOCK.schedule(PLAYER.update)
#===========================================================================#



################################
# ~*~PYGLETS RUN-FUNKSJONER~*~ #
################################
@WINDOW.event
def on_key_press(symbol, modifiers):
	if symbol == key.Q: pyglet.app.exit()
	if symbol == key.W or symbol == key.UP: PLAYER.keys["up"] = True
	if symbol == key.S or symbol == key.DOWN: PLAYER.keys["down"] = True
	if symbol == key.A or symbol == key.LEFT: PLAYER.keys["left"] = True
	if symbol == key.D or symbol == key.RIGHT: PLAYER.keys["right"] = True


@WINDOW.event
def on_key_release(symbol, modifiers):
	if symbol == key.W or symbol == key.UP: PLAYER.keys["up"] = False
	if symbol == key.S or symbol == key.DOWN: PLAYER.keys["down"] = False
	if symbol == key.A or symbol == key.LEFT: PLAYER.keys["left"] = False
	if symbol == key.D or symbol == key.RIGHT: PLAYER.keys["right"] = False


@WINDOW.event
def on_draw():
	WINDOW.clear()
	main_batch.draw()

# trengs ikke før andre objekter enn playeren skal oppdateres
#CLOCK.schedule_interval(update, 120/1.0)
pyglet.app.run()
