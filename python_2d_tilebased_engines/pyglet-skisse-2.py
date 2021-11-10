import sys 
import pyglet

from pyglet.window import key, mouse
# hent sprites på en anen måte, 
# layer dem, 
# lag et nytt spritesheet 
# og så gi det til pyglet
# begynn kanskje med å kutte dem alle opp 
# i en mappe.

MOTION_CONSTANT=48
WIDTH=512
HEIGHT=512
TILESIZE = 32

keys = key.KeyStateHandler()
config = pyglet.gl.Config(sample_buffers=1,samples=2, double_buffer=True, depth_size=0, stencil_size=0)
WINDOW = pyglet.window.Window(width=WIDTH,height=HEIGHT,resizable=True,caption='gamers rising up',config=config, vsync=True)
WINDOW.push_handlers(key)
CLOCK = pyglet.clock
dt = CLOCK.tick()
main_batch = pyglet.graphics.Batch()
SPRITES = []



class Player(pyglet.sprite.Sprite):
	def __init__(self,image, x,y):
		super(Player, self).__init__(image,x,y,batch=main_batch,group=MID_SPRITES)
		self.keys = dict(left=False, right=False, up=False, down=False)
	


	def update(self, dt):
		pass
		#to_moveX = to_moveY = 0

		#if self.keys["up"]: to_moveY = (dt * MOTION_CONSTANT)
		#if self.keys["down"]: to_moveY = -(dt * MOTION_CONSTANT)
		#if self.keys["left"]: to_moveX = -(dt * MOTION_CONSTANT)	
		#if self.keys["right"]: to_moveX = (dt * MOTION_CONSTANT)
		
		#if to_moveX or to_moveY:
		#	self.move(self.x + to_moveX, self.y + to_moveY)
			

#===========================================================================#

pyglet.resource.path = ['./assets']
SPRITESHEET = pyglet.resource.image('rpgsheet.png')
SPRITESHEET2 = pyglet.resource.image('brahladin.png')
GTREE1 = SAND1 = SPRITESHEET.get_region(x=(11 * TILESIZE),y=(11* TILESIZE),width=TILESIZE,height=TILESIZE)
TREE1 =SPRITESHEET.get_region(x=(8 * TILESIZE),y=(13 * TILESIZE),width=TILESIZE,height=TILESIZE)
GRASS1 = SPRITESHEET.get_region(x=(14 * TILESIZE),y=(14* TILESIZE),width=TILESIZE,height=TILESIZE)

GROUND_SPRITES = pyglet.graphics.OrderedGroup(0)
MID_SPRITES = pyglet.graphics.OrderedGroup(1)

PLAYER1 = SPRITESHEET2.get_region(x=(0 * TILESIZE),y=(0 * TILESIZE),width=TILESIZE,height=TILESIZE)
PLAYER = Player(PLAYER1,WIDTH //2,HEIGHT //2)

for y in range(32):
	for x in range(32):
		SPRITES.append(pyglet.sprite.Sprite(GRASS1, x * TILESIZE, y * TILESIZE, batch=main_batch,group=GROUND_SPRITES))
SPRITES.append(PLAYER)


#===========================================================================#
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


def update(dt):
	print("AWDAWDAWD")

@WINDOW.event
def on_draw():
	WINDOW.clear()
	main_batch.draw()

pyglet.clock.schedule_interval(update, 120/1.0)
pyglet.app.run()
