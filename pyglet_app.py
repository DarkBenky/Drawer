import pyglet
from pyglet.window import key
import numpy as np
import random
import time
import mask_gen

class Layers:
    def __init__(self, number_of_layers=5 , screen_width=650, screen_height=500):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layers = [np.zeros((screen_width, screen_height), dtype=bool) for _ in range(number_of_layers)]
        self.colors = [np.zeros((screen_width, screen_height, 3), dtype=np.uint8) for _ in range(number_of_layers)]
        self.last_rendered_layers = None

    def add_items(self, layer: int, mask: np.ndarray, color: tuple):
        star = time.time()
        """
        previous implementation 
        self.layers[layer] |= mask
        self.colors[layer][mask] = color
        """
        self.layers[layer], self.colors[layer] = mask_gen.add_items_cython(self.layers[layer], self.colors[layer], mask, layer, color)
        print('add_items:',time.time()-star)
    

    def remove_items(self, layer: int, mask: np.ndarray):
        self.layers[layer] &= ~mask
        # Reset color to black for removed items
        self.colors[layer][mask] = (0, 0, 0)
    
    def return_img(self, render_current: bool, current_layer: int):
        start = time.time()
        img = np.zeros((self.screen_width, self.screen_height, 3), dtype=np.uint8)
        
        # Check if rendering only the current layer
        if render_current:
            img[self.layers[current_layer]] = self.colors[current_layer][self.layers[current_layer]]
        else:
            # Check if layers have changed since last render
            if self.last_rendered_layers is not None:
                if all(np.array_equal(layer1, layer2) for layer1, layer2 in zip(self.layers, self.last_rendered_layers)):
                    # No changes, return the previous image
                    print('return_img:', time.time() - start)
                    return self.last_rendered_image
            
            # Render all layers
            for layer in range(len(self.layers)):
                img[self.layers[layer]] = self.colors[layer][self.layers[layer]]
            
            # Cache the rendered layers and image
            self.last_rendered_layers = [layer.copy() for layer in self.layers]
            self.last_rendered_image = img
        
        print('return_img:', time.time() - start)
        return img
    
    def draw(self, layer: int, x: int, y: int, radius: int, color: tuple):
        # Create a circular mask
        start = time.time()
        # mask = np.zeros((screen_width, screen_height), dtype=bool)
        # r = radius ** 2
        # for i in range(-radius, radius):
        #     for j in range(-radius, radius):
        #         if i ** 2 + j ** 2 < r:
        #             new_x = x + i
        #             new_y = y + j
        #             if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
        #                 mask[new_x, new_y] = True
        mask = mask_gen.draw_cython(x, y, radius, color , self.screen_width, self.screen_height)

        print('draw:',time.time()-start)
        # Add items with a copy of the mask
        self.add_items(layer, mask.copy(), color)

    def clear(self):
        for i in range(len(self.layers)):
            self.layers[i].fill(False)
            self.colors[i][:] = (0, 0, 0) 

screen_width = 650
screen_height = 500

num_layers = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR = (255, 0, 0)


layers = Layers(num_layers, screen_width, screen_height)



# Initialize Pyglet window and other variables
config = pyglet.gl.Config(double_buffer=True ,major_version = 3, minor_version = 3, depth_size = 16)
window = pyglet.window.Window(screen_width, screen_height, config=config)
current_layer = 0
render_current = False
drawing = False
radius = 5

frames = 0
fps_display = pyglet.window.FPSDisplay(window)

fps_display_label = pyglet.text.Label('', font_size=12, x=10, y=10, anchor_x='left', anchor_y='bottom')

@window.event
def on_draw():
    window.clear()
    image_data = layers.return_img(render_current=render_current, current_layer=current_layer)
    image_data_transposed = np.transpose(image_data, (1, 0, 2))

    # Convert the image data to bytes
    image_data_bytes = image_data_transposed.astype(np.uint8).tobytes()

    image = pyglet.image.ImageData(screen_width, screen_height, 'RGB', image_data_bytes)
    image.blit(0, 0)
    
    fps_display.draw()

@window.event
def on_key_press(symbol, modifiers):
    global current_layer, render_current, COLOR
    if symbol == key.C:
        layers.clear()
    elif symbol == key.S:
        pyglet.image.save(window.canvas, "drawing.png")
    elif symbol == key.UP:
        current_layer = min(current_layer + 1, num_layers)
        print(f'{current_layer=}')
    elif symbol == key.DOWN:
        current_layer = max(current_layer - 1, 0)
        print(f'{current_layer=}')
    elif symbol == key.R:
        COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        print(f'{COLOR=}')
    elif symbol == key.SPACE:
        render_current = not render_current
        print(f'{render_current=}')

@window.event
def on_mouse_press(x, y, button, modifiers):
    global drawing
    if button == pyglet.window.mouse.LEFT:
        drawing = True
    
@window.event  
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global radius
    if scroll_y > 0:
        radius = min(radius + 1, 50)
        print(f'Radius increased: {radius}')
    elif scroll_y < 0:
        radius = max(radius - 1, 1)
        print(f'Radius decreased: {radius}')

@window.event
def on_mouse_release(x, y, button, modifiers):
    global drawing
    if button == pyglet.window.mouse.LEFT:
        drawing = False

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global drawing
    if drawing:
        layers.draw(current_layer, x, y, radius, COLOR)

# Run Pyglet application
pyglet.app.run()
