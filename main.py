import pygame
import numpy as np
import random
import time
import mask_gen
import pygame_gui


# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 600
screen_height = 400
num_layers = 5
global screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Drawing App")
gui_manager = pygame_gui.UIManager((screen_width, screen_height)) 

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR = (255, 0, 0)


def draw_gui(current_selection : str , brush_size :str):
    gui_manager.clear_and_reset()
    label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10),(100,50)), text=current_selection, manager=gui_manager)
    brush_size_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((90, 10),(140,50)), text='brush size: '+brush_size, manager=gui_manager)
    gui_manager.update(1)
    gui_manager.draw_ui(screen)


class Layers:
    def __init__(self, number_of_layers=5 , screen_width=650, screen_height=500):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layers = np.zeros((num_layers,screen_width, screen_height), dtype=bool)
        self.colors = np.zeros((num_layers,screen_width, screen_height, 3), dtype=np.uint8)
        self.last_rendered_layers = None
        self.update = False
        self.last_rendered_layer = None
        # self.count : int = 0
        # self.render_v1 : float = 0.2
        # self.render_v2 : float = 0.0
    
    def merge_all_layers(self):
        # Create an empty merged layer
        merged_layer = np.zeros((self.screen_width, self.screen_height), dtype=bool)
        merged_color = np.zeros((self.screen_width, self.screen_height, 3), dtype=np.uint8)

        # Merge all layers into one
        for layer, color in zip(self.layers, self.colors):
            merged_layer |= layer
            merged_color[layer] = color[layer]

        # clear all layers
        self.clear()
        
        # Save the merged layer as layer 0
        self.layers[0] = merged_layer
        self.colors[0] = merged_color
        

    def add_items(self, layer: int, mask: np.ndarray, color: tuple):
        # star = time.time()
        """
        previous implementation 
        self.layers[layer] |= mask
        self.colors[layer][mask] = color
        """
        self.layers[layer], self.colors[layer] = mask_gen.add_items_cython(self.layers[layer], self.colors[layer], mask, color)
        # print('add_items:',time.time()-star)
    

    def remove_items(self, layer: int, mask: np.ndarray):
        # self.layers[layer] &= ~mask
        # # Reset color to black for removed items
        # self.colors[layer][mask] = (0, 0, 0)
        self.layers[layer], self.colors[layer] = mask_gen.remove_cython(self.layers[layer], self.colors[layer], mask)
    
    def return_img(self, render_current: bool, current_layer: int):
        # start = time.time()
        img = np.zeros((self.screen_width, self.screen_height, 3), dtype=np.uint8)
        
        # Check if rendering only the current layer
        if render_current:
            if self.last_rendered_layer is not None and self.update is False:
                if np.array_equal(self.layers[current_layer], self.last_rendered_layer):
                    return self.last_rendered_image_single
            else:
                img = mask_gen.draw_layer_cython(self.layers,self.colors,current_layer)
                self.last_rendered_layer = self.layers[current_layer]
                self.last_rendered_image_single = img
                self.update = False
            # img[self.layers[current_layer]] = self.colors[current_layer][self.layers[current_layer]]
        else:
            # Check if layers have changed since last render
            if self.last_rendered_layers is not None and self.update is False:
                if np.array_equal(self.layers, self.last_rendered_layers):
                    # No changes, return the previous image
                    # print('return_img:', time.time() - start), lenght
                    return self.last_rendered_image
            else:
                # self.count += 1
                # start = time.time()
                # for layer in range(len(self.layers)):
                #     img[self.layers[layer]] = self.colors[layer][self.layers[layer]]
                # self.render_v1 += time.time() - start
                # print('render V-1 time:', self.render_v1/self.count)
                # start = time.time()
                img = mask_gen.draw_layers_cython(self.layers,self.colors)
                # self.render_v2 += time.time() - start
                # print('render V-2 time:', self.render_v2/self.count)
                
                # Cache the rendered layers and image
                self.last_rendered_layers = self.layers
                self.last_rendered_image = img
                self.update = False
        
        # print('return_img:', time.time() - start)
        return img
    
    def blur(self, x : int, y : int, radius: int , layer: int):
        mask = mask_gen.box_mask_cython(x, y, radius, self.screen_width, self.screen_height)
        
        colors = self.colors[layer][mask]
        length = colors.shape[0]
        size = int(np.ceil(np.sqrt(length)))
        
        rows = length // size
        cols = size if length % size == 0 else size + 1
        
        # Reshape the array to the closest box shape
        reshaped_arr = np.resize(colors, (rows, cols , 3))

        # Average the colors
        colors = mask_gen.blur_cython(reshaped_arr, radius // 2)
        colors = np.resize(colors, (length, 3))
        
        self.colors[layer][mask] = colors
        self.update = True
        
        
    def contrast(self, x : int, y : int, radius: int , layer: int , factor: int = 1.05):
        mask = mask_gen.box_mask_cython(x, y, radius, self.screen_width, self.screen_height)
        
        colors = self.colors[layer][mask]
        length = colors.shape[0]
        size = int(np.ceil(np.sqrt(length)))
        
        rows = length // size
        cols = size if length % size == 0 else size + 1
        
        # Reshape the array to the closest box shape
        reshaped_arr = np.resize(colors, (rows, cols , 3))

        colors = mask_gen.increase_contrast_cython(reshaped_arr, factor)
        print(colors)
        colors = np.resize(colors, (length, 3))
        
        self.colors[layer][mask] = colors
        self.update = True
        
    def contrast_circle(self, x : int, y : int, radius: int , layer: int , factor: int = 1.05):
        mask = mask_gen.draw_cython(x, y, radius, self.screen_width, self.screen_height)
        
        colors = self.colors[layer][mask]
        length = colors.shape[0]
        size = int(np.ceil(np.sqrt(length)))
        
        rows = length // size
        cols = size if length % size == 0 else size + 1
        
        # Reshape the array to the closest box shape
        reshaped_arr = np.resize(colors, (rows, cols , 3))

        colors = mask_gen.increase_contrast_cython(reshaped_arr, factor)
        print(colors)
        colors = np.resize(colors, (length, 3))
        
        self.colors[layer][mask] = colors
        self.update = True
    
    # TODO: Fix this method
    def edge(self, x : int, y : int, radius: int , layer: int , color: tuple, threshold: int):
        mask = mask_gen.box_mask_cython(x, y, radius, self.screen_width, self.screen_height)
        
        colors = self.colors[layer][mask]
        length = colors.shape[0]
        size = int(np.ceil(np.sqrt(length)))
        
        rows = length // size
        cols = size if length % size == 0 else size + 1
        
        # Reshape the array to the closest box shape
        reshaped_arr = np.resize(colors, (rows, cols , 3))

        colors = mask_gen.edge_cython(reshaped_arr , COLOR , threshold)
        colors = np.resize(colors, (length, 3))
        
        self.colors[layer][mask] = colors
        self.update = True
        
    def blur_circle(self, x : int, y : int, radius: int , layer: int):
        mask = mask_gen.draw_cython(x, y, radius, self.screen_width, self.screen_height)
        
        colors = self.colors[layer][mask]
        length = colors.shape[0]
        size = int(np.ceil(np.sqrt(length)))
        
        rows = length // size
        cols = size if length % size == 0 else size + 1
        
        # Reshape the array to the closest box shape
        reshaped_arr = np.resize(colors, (rows, cols , 3))

        # Average the colors
        colors = mask_gen.blur_cython(reshaped_arr, radius // 1.5)
        colors = np.resize(colors, (length, 3))
        
        self.colors[layer][mask] = colors
        self.update = True

    def draw(self, layer: int, x: int, y: int, radius: int, color: tuple):
        # Create a circular mask
        # start = time.time()
        # mask = np.zeros((screen_width, screen_height), dtype=bool)
        # r = radius ** 2
        # for i in range(-radius, radius):
        #     for j in range(-radius, radius):
        #         if i ** 2 + j ** 2 < r:
        #             new_x = x + i
        #             new_y = y + j
        #             if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
        #                 mask[new_x, new_y] = True
        mask = mask_gen.draw_cython(x, y, radius, self.screen_width, self.screen_height)

        # print('draw:',time.time()-start)
        # Add items with a copy of the mask
        self.update = True
        self.add_items(layer, mask.copy(), color)
        
    def draw_box(self, layer: int, x: int, y: int, radius: int, color: tuple):
        # Create a circular mask
        # start = time.time()
        # mask = np.zeros((screen_width, screen_height), dtype=bool)
        # r = radius ** 2
        # for i in range(-radius, radius):
        #     for j in range(-radius, radius):
        #         if i ** 2 + j ** 2 < r:
        #             new_x = x + i
        #             new_y = y + j
        #             if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
        #                 mask[new_x, new_y] = True
        mask = mask_gen.box_mask_cython(x, y, radius, self.screen_width, self.screen_height)

        # print('draw:',time.time()-start)
        # Add items with a copy of the mask
        self.update = True
        self.add_items(layer, mask.copy(), color)    

    def clear(self):
        for i in range(len(self.layers)):
            self.layers[i].fill(False)
            self.colors[i][:] = (0, 0, 0) 


layers = Layers(num_layers, screen_width, screen_height)

# Set up the drawing variables
drawing = False
erasing = False
averaging = False
averaging_circle = False
contrast = False
contrast_circle = False
drawing_box = False
erase_box = False
edge = False

radius = 5

clock = pygame.time.Clock()


# Game loop
running = True
current_layer = 0
render_current = False

tools = ['draw', 'draw box' , 'erase' , 'erase box', 'blur' , 'blur circle' , 'contrast' , 'contrast circle' , 'edge']
current_tool = 0
current_selected_tool = tools[current_tool]

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                layers.clear() 
            elif event.key == pygame.K_s:
                pygame.image.save(screen, "drawing.png")
            elif event.key == pygame.K_UP:
                current_layer = min(current_layer + 1, num_layers-1)
                layers.update = True
                print(f'{current_layer=}')
            elif event.key == pygame.K_DOWN:
                current_layer = max(current_layer - 1, 0)
                layers.update = True
                print(f'{current_layer=}')
            elif event.key == pygame.K_r:
                COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                print(f'{COLOR=}')
            elif event.key == pygame.K_SPACE:
                render_current = not render_current
                print(f'{render_current=}')
                layers.update = True
            elif event.key == pygame.K_m:
                current_layer = 0
                layers.merge_all_layers()
            # elif event.key == pygame.K_t:
            #     current_tool = (current_tool + 1) % len(tools)
            #     print(f'{tools[current_tool]=}')
            #     current_selected_tool = tools[current_tool]       
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                pos = pygame.mouse.get_pos()
                # layers.draw(current_layer,pos[0],pos[1],radius,COLOR)
                # drawing = True
                if current_selected_tool == 'draw':
                    layers.draw(current_layer,pos[0],pos[1],radius,COLOR)
                    drawing = True
                elif current_selected_tool == 'erase':
                    layers.remove_items(current_layer, mask_gen.draw_cython(pos[0], pos[1], radius, screen_width, screen_height))
                    erasing = True
                elif current_selected_tool == 'blur':
                    layers.blur(pos[0], pos[1], radius, current_layer)
                    averaging = True
                elif current_selected_tool == 'blur circle':
                    layers.blur_circle(pos[0], pos[1], radius, current_layer)
                    averaging_circle = True
                elif current_selected_tool == 'contrast':
                    layers.contrast(pos[0], pos[1], radius, current_layer)
                    contrast = True
                elif current_selected_tool == 'contrast circle':
                    layers.contrast_circle(pos[0], pos[1], radius, current_layer)
                    contrast_circle = True
                elif current_selected_tool == 'draw box':
                    layers.draw_box(current_layer,pos[0],pos[1],radius,COLOR)
                    drawing_box = True
                elif current_selected_tool == 'erase box':
                    layers.remove_items(current_layer, mask_gen.box_mask_cython(pos[0], pos[1], radius, screen_width, screen_height))
                    erase_box = True
                elif current_selected_tool == 'edge':
                    layers.edge(pos[0], pos[1], radius, current_layer , COLOR , 1.5)
                    edge = True
                
            elif event.button == 4: # Scroll up
                radius = min(radius + 1, 50)
                print(f'{radius=}')
            elif event.button == 5: # Scroll down
                radius = max(radius - 1, 1)
                print(f'{radius=}')
                
            elif event.button == 3: # Right mouse button
                current_tool = (current_tool + 1) % len(tools)
                print(f'{tools[current_tool]=}')
                current_selected_tool = tools[current_tool]
                
            # elif event.button == 2: # Middle mouse button
            #     pos = pygame.mouse.get_pos()
            #     layers.blur(pos[0], pos[1], radius, current_layer)
            #     print('average')
            #     averaging = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                drawing = False
                erasing = False
                averaging = False
                averaging_circle = False
                contrast = False
                contrast_circle = False
                drawing_box = False
                erase_box = False
                edge = False
                
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                pos = pygame.mouse.get_pos()
                layers.draw(current_layer,pos[0],pos[1],radius,COLOR)
            elif erasing:
                pos = pygame.mouse.get_pos()
                layers.remove_items(current_layer, mask_gen.draw_cython(pos[0], pos[1], radius, screen_width, screen_height))
            elif averaging:
                pos = pygame.mouse.get_pos()
                layers.blur(pos[0], pos[1], radius, current_layer)
            elif averaging_circle:
                pos = pygame.mouse.get_pos()
                layers.blur_circle(pos[0], pos[1], radius, current_layer)
            elif contrast:
                pos = pygame.mouse.get_pos()
                layers.contrast(pos[0], pos[1], radius, current_layer)
            elif contrast_circle:
                pos = pygame.mouse.get_pos()
                layers.contrast_circle(pos[0], pos[1], radius, current_layer)
            elif drawing_box:
                pos = pygame.mouse.get_pos()
                layers.draw_box(current_layer,pos[0],pos[1],radius,COLOR)
            elif erase_box:
                pos = pygame.mouse.get_pos()
                layers.remove_items(current_layer, mask_gen.box_mask_cython(pos[0], pos[1], radius, screen_width, screen_height))
            elif edge:
                pos = pygame.mouse.get_pos()
                layers.edge(pos[0], pos[1], radius, current_layer , COLOR , 1.5)
                
    # start = time.time()
    screen.blit(pygame.surfarray.make_surface(layers.return_img(render_current=render_current,current_layer=current_layer)), (0, 0))
    
    # draw gui
    draw_gui(tools[current_tool], str(radius))
    
    pygame.display.flip()
    # print('blit:',time.time()-start)
    
    
    
    # Cap the frame rate and show FPS on title
    clock.tick(1024)  # Cap at 60 FPS
    pygame.display.set_caption(f"Pygame FPS Demo - FPS: {clock.get_fps()}")

    # print('fps:',clock.get_fps())  # Print FPS to console
    

# Quit Pygame
pygame.quit()