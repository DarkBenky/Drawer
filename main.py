import pygame
import numpy as np
import random
import time
import mask_gen



# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 650
screen_height = 500
num_layers = 5
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Drawing App")

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR = (255, 0, 0)






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


layers = Layers(num_layers, screen_width, screen_height)

# Set up the drawing variables
drawing = False
radius = 5

clock = pygame.time.Clock()


# Game loop
running = True
current_layer = 0
render_current = False

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
                print(f'{current_layer=}')
            elif event.key == pygame.K_DOWN:
                current_layer = max(current_layer - 1, 0)
                print(f'{current_layer=}')
            elif event.key == pygame.K_r:
                COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                print(f'{COLOR=}')
            elif event.key == pygame.K_SPACE:
                render_current = not render_current
                print(f'{render_current=}')
            
        
            
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                drawing = True
            elif event.button == 4:
                radius = min(radius + 1, 50)
                print(f'{radius=}')
            elif event.button == 5:
                radius = max(radius - 1, 1)
                print(f'{radius=}')
            
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                drawing = False
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                pos = pygame.mouse.get_pos()
                layers.draw(current_layer,pos[0],pos[1],radius,COLOR)
    
    start = time.time()
    screen.blit(pygame.surfarray.make_surface(layers.return_img(render_current=render_current,current_layer=current_layer)), (0, 0))
    pygame.display.flip()
    print('blit:',time.time()-start)
    
    # Cap the frame rate and show FPS on title
    clock.tick(1024)  # Cap at 60 FPS
    pygame.display.set_caption(f"Pygame FPS Demo - FPS: {clock.get_fps()}")

    # print('fps:',clock.get_fps())  # Print FPS to console
    

# Quit Pygame
pygame.quit()