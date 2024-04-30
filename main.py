import pygame
import numpy as np
import random
import time



# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 650
screen_height = 500
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
        self.lookup = {}

    def add_items(self, layer: int, mask: np.ndarray, color: tuple):
        star = time.time()
        self.layers[layer] |= mask
        self.colors[layer][mask] = color
        print('add_items:',time.time()-star)
    

    def remove_items(self, layer: int, mask: np.ndarray):
        self.layers[layer] &= ~mask
        # Reset color to black for removed items
        self.colors[layer][mask] = (0, 0, 0)
    
    def return_img(self):
        start = time.time()
        img = np.zeros((screen_width, screen_height, 3), dtype=np.uint8)
        for layer in range(len(self.layers)):
            img[self.layers[layer]] = self.colors[layer][self.layers[layer]]
        print('return_img:',time.time()-start)
        return img
    
    def draw(self, layer: int, x: int, y: int, radius: int, color: tuple):
        # Create a circular mask
        start = time.time()
        mask = np.zeros((screen_width, screen_height), dtype=bool)
        r = radius ** 2
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                if hash((i,j)) in self.lookup:
                    new_x = x + i
                    new_y = y + j
                    if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
                        mask[new_x, new_y] = True
                elif i ** 2 + j ** 2 < r:
                    self.lookup[hash((i,j))] = True
                    new_x = x + i
                    new_y = y + j
                    if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
                        mask[new_x, new_y] = True

        print('draw:',time.time()-start)
        # Add items with a copy of the mask
        self.add_items(layer, mask.copy(), color)

    def clear(self):
        for i in range(len(self.layers)):
            self.layers[i].fill(False)
            self.colors[i][:] = (0, 0, 0) 


layers = Layers()

# Set up the drawing variables
drawing = False
radius = 5

clock = pygame.time.Clock()


# Game loop
running = True
current_layer = 0
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
                current_layer = min(current_layer + 1, 9)
                print(f'{current_layer=}')
            elif event.key == pygame.K_DOWN:
                current_layer = max(current_layer - 1, 0)
                print(f'{current_layer=}')
            elif event.key == pygame.K_r:
                COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                print(f'{COLOR=}')
        
            
        
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
    

    screen.blit(pygame.surfarray.make_surface(layers.return_img()), (0, 0))
    pygame.display.flip()
    
    # Cap the frame rate and show FPS on title
    clock.tick(120)  # Cap at 60 FPS
    pygame.display.set_caption(f"Pygame FPS Demo - FPS: {clock.get_fps()}")

    # print('fps:',clock.get_fps())  # Print FPS to console
    

# Quit Pygame
pygame.quit()