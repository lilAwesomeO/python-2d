import math
#import random
#from pyrr import Matrix44, Quaternion, Vector3, vector

import moderngl as mgl           #https://moderngl-window.readthedocs.io/en/latest/
import moderngl_window as mglw   #https://github.com/moderngl/moderngl/blob/master/examples/multiple_instance_rendering.py 
from moderngl_window.conf import settings
from moderngl_window.timers.clock import Timer
from moderngl_window.utils.scheduler import Scheduler

from numpy.random import default_rng
#from sys import intern
import numpy as np
#import numba
from PIL import Image

SIZE_X = 800
SIZE_Y = 600

START = -6400
END= 6400
STEP = 32
ROW = END // STEP
SHRINK = 32

#@numba.jit(fastmath=True, parallel=True)
def tree_map():
    t_arr = np.array([])
    rng = default_rng()
    x_offset_spawn = y_offset_spawn = 0
    for y in range(START // STEP,END // STEP):
    #for y in numba.prange(START // STEP,END // STEP):
        rand_src = rng.standard_normal(END * 2 // STEP)
        for x in range(START // STEP,END // STEP):
        #for x in numba.prange(START // STEP,END // STEP):
            if rand_src[x + (END // STEP)] > 1.75 and (x_offset_spawn <= 0 and y_offset_spawn <= 0):
                t_arr = np.append((x * (STEP / SHRINK), (y * (STEP / SHRINK)), 2.0),t_arr).astype(dtype="f4")
            
    return t_arr
#@numba.jit(fastmath=True, parallel=True)
def get_map_arr():
    n_arr_x = np.divide(np.arange(START, END, STEP, dtype="f4"),SHRINK)
    n_zeros = np.ones((END*2)//STEP,dtype="f4")
    n_arr = np.column_stack((n_arr_x,n_zeros))
    n_arr_big = None

    #for x in numba.prange(-ROW,ROW):
    for x in range(-ROW,ROW):
        n_arr_big = np.append(n_arr_big,np.hstack((np.full((ROW*2,1),x * (STEP / SHRINK)),n_arr))).astype("f4")
    
    n_arr_big = np.append(n_arr_big,tree_map()).astype(dtype="f4")
    ###### player, de to første floats er bare dummies(could they be something else like direction/animation?)
    #n_arr_big = np.append(n_arr_big,(0.0,0.0,0.0)).astype(dtype="f4")
    
    return np.delete(n_arr_big,0)#np.append(np.array([0.0,0.0,0.0]),np.delete(n_arr_big,0))

MAP_COORDS = get_map_arr()
INSTANCE_AMOUNT = (len(MAP_COORDS) + 3) // 3
#conver til å dekke hele altså fra -1 til 1?
VERTECIES = np.array([
    #vertex,    texture-coord
    0.5, 0.5,   #1.0, 1.0,   
    0.5, -0.5,  #1.0, -1.0,   
    -0.5, -0.5, #-1.0, -1.0,   
    -0.5, 0.5,  #-1.0, 1.0,  
    ])
RENDER_INDICIES = np.array([
    0, 1, 3, 
    1, 2, 3
    ])
#TREE_PIC = Image.open("C:\\Users\\yo\\Desktop\\devvings\\assets\\rpgsheet.png")
TREE_PIC = Image.open("./rpgsheet.bmp")
TREE_PIC_TEXTURE = TREE_PIC.crop((8*STEP,1*STEP,9*STEP,2*STEP)).transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')
PIC = Image.open("./brahladin.bmp")
PIC = PIC.transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')
OTHER_PIC = Image.open("./gr33n.bmp")
OTHER_PIC = OTHER_PIC.transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')



class CustomSetup:    
    #@numba.jit()
    def __init__(self):

        # Configure to use pyglet window
        settings.WINDOW['class'] = 'moderngl_window.context.pyglet.Window'
        settings.WINDOW['gl_version'] = (4, 0)
        settings.WINDOW['size'] = (SIZE_X,SIZE_Y)
        settings.WINDOW['aspect_ratio'] = SIZE_X / SIZE_Y
        settings.WINDOW['title'] = "__<=<=<´-´>=>=>__/´/\,,,,,,...###__<\¤(=(¤<\__###...,,,,,,/´/\__<=<=<´-´>=>=>__"
        settings.WINDOW['clear_color'] = (0)
        settings.WINDOW['vsync'] = False
        settings.WINDOW['log_level'] = None

        self.X_POINTS = 0
        self.Y_POINTS = 0
        self.wnd = mglw.create_window_from_settings()
        self.wnd.key_event_func = self.key_event
        self.ctx = self.wnd.ctx
        self.ctx.wireframe = False
        self.ctx.enable(self.ctx.BLEND | self.ctx.CULL_FACE)
        self.ctx.cull_face = 'front'
        #self.ctx.multisample = True
        #self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA

        self.prog = self.ctx.program(
           vertex_shader="""   
                #version 330
                
                in vec2 in_pos; 
                in float in_texid;
                in vec2 in_vert;
                uniform vec2 pos;
                
                out vec3 out_texinfo;
                
                void main() {
                    gl_Position = vec4(pos + (in_vert + in_pos), 0.0, 4.0);
                    out_texinfo = vec3(in_vert,in_texid);
                }
            """
            ,
            fragment_shader="""
                #version 330    
            
                uniform sampler2DArray Texture;
                
                in vec3 out_texinfo;
                out vec4 outColor;

                void main() {
                    outColor = texture(Texture, vec3(out_texinfo.xy +0.5, out_texinfo.z));
            }
            """,   
        )

        """
            x og y til np-array
            bit-degree-dict for movement
            så gang degrees * frame_time og add det til x og y
            null X_POINTS

            time som self-var? i np arr for speed?
        """
        self.P_COORDS_X = 0.0
        self.P_COORDS_Y = 0.0
        self.prog['pos'] = (self.P_COORDS_X, self.P_COORDS_Y)

        """
        self.g_pos = self.prog['GameIn']
        self.g_pos.binding = 0

        self.toGpuBuffer = self.ctx.buffer(reserve=self.g_pos.size)
        self.toGpuBuffer.bind_to_uniform_block(0)
        self.toGpuBuffer.write(np.array([0,0]).tobytes())
        """

        images = [
            PIC,
            OTHER_PIC,
            TREE_PIC_TEXTURE,
        ]

        depth = len(images)
        dataList = []

        for image in images:
            if 32 != image.size[0] or 32 != image.size[1]:
                raise ValueError(f"image size mismatch: {image.size[0]}x{image.size[1]}")
            
            dataList.append(list(image.getdata()))
        
        imageArrayData = np.array(dataList, np.uint8).tobytes()
        components = 4

        self.tex = self.ctx.texture_array((32, 32, depth),components, imageArrayData, alignment=1)
        self.prog["Texture"] = 0
       # self.tex.build_mipmaps()
       # self.tex.filter=(mgl.NEAREST,mgl.NEAREST)
        self.tex.repeat_x = self.tex.repeat_y = False
        self.tex.use(location=0)

        self.vertex_buffer = self.ctx.buffer(VERTECIES.astype("f4").tobytes())
        self.pos_buffer = self.ctx.buffer(MAP_COORDS.astype("f4").tobytes())
        self.index_buffer = self.ctx.buffer(RENDER_INDICIES.astype("i4").tobytes())
        self.actor_vertex = self.ctx.buffer(
                    np.array([
                        -self.P_COORDS_X,
                        -self.P_COORDS_Y, 
                        0.0
                        ]).astype("f4").tobytes(), dynamic=True)


        self.vao_content = [
            (self.vertex_buffer, '2f', 'in_vert'),
            (self.pos_buffer, '2f 1f/i', 'in_pos', "in_texid"),
        ]

        self.vao = self.ctx.vertex_array(self.prog, self.vao_content, self.index_buffer)

        self.t = self.ctx.vertex_array(
            self.prog,[
                (self.vertex_buffer, '2f', 'in_vert'),
                (self.actor_vertex, '2f 1f/i',"in_pos","in_texid"),
                ],
            self.index_buffer,)

    #self.toGpuBuffer.write(self.P_COORDS.astype(dtype=np.float32).tobytes())
    #
        
    def run(self):
        self.timer = Timer()
        self.timer.start()
        self.last_frame = 0
        self.update_delay = 1 / 60  # updates per second
        self.last_updated = 0
        #self.acc = 1.6
        #self.fric = 4.8

        while not self.wnd.is_closing:
            self.wnd.clear()
            self.time, self.last_frame = self.timer.next_frame()

            # First VAO, contains static map-data
            self.prog["pos"] = (self.P_COORDS_X, self.P_COORDS_Y)
            self.P_COORDS_X += self.X_POINTS
            self.P_COORDS_Y += self.Y_POINTS
            self.vao.render(instances=INSTANCE_AMOUNT)

            # second VAO contains moving data
            self.actor_vertex.write(
                np.array([
                    -self.P_COORDS_X,
                    -self.P_COORDS_Y, 
                    0.0
                    ]).astype("f4").tobytes()
                )                
            self.t.render()    
            self.actor_vertex.orphan(self.actor_vertex.size)
            
            if self.time - self.last_updated > self.update_delay:
                self.last_updated = self.time 

            self.wnd.swap_buffers()

        self.wnd.destroy()
    
    def key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_RELEASE:
            if key == self.wnd.keys.W:
                self.Y_POINTS = 0
            if key == self.wnd.keys.A:
                self.X_POINTS = 0
            if key == self.wnd.keys.S:
                self.Y_POINTS = 0
            if key == self.wnd.keys.D:
                self.X_POINTS = 0
    
        elif action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.A:
                self.X_POINTS += self.last_frame
            if key == self.wnd.keys.S:
                self.Y_POINTS += self.last_frame 
            if key == self.wnd.keys.D:
                self.X_POINTS -= self.last_frame 
            if key == self.wnd.keys.W:
                self.Y_POINTS -= self.last_frame 
        
if __name__ == '__main__':
    app = CustomSetup()
    app.run()
    