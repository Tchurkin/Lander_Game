import pygame
import math




# Initialize Pygame
pygame.init()

# Set up game window
WIDTH, HEIGHT = 1920, 1080
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lunar Lander Game")
FPS = 60


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (158, 157, 157)

# Gameplay settings
fps_counter = True

# Clock for managing the frame rate
clock = pygame.time.Clock()

# Environment settings
gravity = 10
friction = 10 #divide speed by this when on ground





def load_images(lander):
    global lander_imgs
    global explosion_imgs
    
    for i in range(0,lander.img_num):
        image = pygame.image.load(f'lander{i}.png')
        image = pygame.transform.scale(image, (lander.width, lander.height))
        lander_imgs.append(image)
        
    for i in range(0,lander.explosions_num):
        image = pygame.image.load(f'explosion{i}.png')
        image = pygame.transform.scale(image, (lander.width*2, lander.height*2))
        explosion_imgs.append(image)



def text(X, Y, name, display):
    
    # Font for display
    font = pygame.font.Font(None, 24)

    text = font.render(f"{name}: {round(display, 2)}", True, BLACK)
    text_rect = text.get_rect(topright=(X, Y))
    window.blit(text, text_rect)





    
class Platform:

    def __init__(self, height, width, X, Y, color):
        self.height = height
        self.width = width
        self.X = X
        self.Y = Y
        self.color = color

platform_1 = Platform(10, 200, 300, 500, GRAY)
platform_2 = Platform(10, 400, 1000, 1000, GRAY)
platform_3 = Platform(10, 50, 800, 400, GRAY)

platform_num = 3

# Update platforms to be a list of Platform objects
platforms = []
n = 1
while n <= platform_num:
    platforms.append(globals()["platform_" + str(n)])
    n += 1
    
def render_platforms(platforms):
    for platform in platforms:
        pygame.draw.rect(window, platform.color, (platform.X, platform.Y, platform.width, platform.height))


class Lander:

    def __init__(self, height, width, X, Y, vel_x, vel_y, rot, thrust, weight, rot_speed, img_name, img_num, explosions_name, explosions_num):
        self.height = height
        self.width = width
        self.X = X
        self.Y = Y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.rot = rot
        self.thrust = thrust
        self.weight = weight
        self.rot_speed = rot_speed
        self.img_name = img_name
        self.img_num = img_num
        self.explosions_name = explosions_name
        self.explosions_num = explosions_num
    

    def physics_control(self):

        accel_x = 0
        accel_y = 0
        
        # Constrain rotation to the range of 0 to 180 degrees
        if self.rot < 0:
            self.rot += 360
        if self.rot > 180:
            self.rot -= 360
        
        # Calculate the thrust acceleration based on the rotation angle
        if keys[pygame.K_UP]:
            accel_x += math.sin(math.radians(self.rot)) * (-self.thrust/self.weight) / frame_rate
            accel_y += math.cos(math.radians(self.rot)) * (-self.thrust/self.weight) / frame_rate
            
        # Rotate counter-clockwise when pressing left
        if keys[pygame.K_LEFT]:
            self.rot += self.rot_speed / frame_rate
            
        # Rotate clockwise when pressing right
        if keys[pygame.K_RIGHT]:
            self.rot -= self.rot_speed / frame_rate
        
        # Apply gravity
        accel_y += gravity / frame_rate


        # Update velocity based on acceleration
        self.vel_x += accel_x
        self.vel_y += accel_y
        
        # Update position based on velocity
        self.X += self.vel_x
        self.Y += self.vel_y
        

lander = Lander(30, 30, WIDTH // 2 - 30 // 2, HEIGHT - 30, 0, 0, 0, 1800, 100, 180, 'lander', 3, 'explosion', 2)


def boundaries(lander, platforms):
    lander.top = (lander.Y)
    lander.bottom = (lander.Y + lander.height)
    lander.left = (lander.X)
    lander.right = (lander.X + lander.width)

    # Loop through the list to set properties for all platforms
    for platform in platforms:
        platform.top = platform.Y
        platform.bottom = platform.Y + platform.height
        platform.left = platform.X
        platform.right = platform.X + platform.width

def touching():
    
    boundaries(lander, platforms)

    platform_col = 0

    collision = False
    
    for platform in platforms:

        platform_col += 1
        
        if (collision == False) and (lander.right > platform.left) and (lander.left < platform.right) and (lander.bottom > platform.top) and (lander.top < platform.bottom):
            collision = True

        if collision == False:
            platform_col = 0
        return platform_col



def collision_detection(lander, platforms):

    global alive, explosion_rot

    boundaries(lander, platforms)
    for platform in platforms:
        
        if lander.bottom >= platform.top and lander.bottom <= platform.bottom and lander.right >= platform.left and lander.left <= platform.right:

            lander.Y = platform.top - lander.height

            if lander.rot < -30 or lander.rot > 30:
                alive = False
                
            if lander.vel_y <= 5:
                lander.vel_y = 0
                lander.vel_x = lander.vel_x / (friction**(1/60))
                if lander.rot <= 30 and lander.rot >= 0 or lander.rot >= -30 and lander.rot <= 0:
                    lander.rot /= 1.5    
            else:
                alive = False

            if alive == False:
                explosion_rot = 0


        if lander.top >= platform.top and lander.top <= platform.bottom and lander.right >= platform.left and lander.left <= platform.right:
            
            lander.Y = platform.bottom

                
            if lander.vel_y >= -5:
                lander.vel_y = 0
                lander.vel_x = lander.vel_x / (friction**(1/60))
                if lander.rot <= 30 and lander.rot >= 0 or lander.rot >= -30 and lander.rot <= 0:
                    lander.rot /= 1.5   
            else:
                alive = False
                
            if alive == False:
                explosion_rot = 180

def render_lander(lander_img, lander_burns):

    global burn_frame, last_update

        
    # Initialize lander image with the default image
    lander_image = lander_img
    
    # Set burn image of lander
    if keys[pygame.K_UP]:
        if current_time - last_update >= 200:
            burn_frame = (burn_frame + 1) % len(lander_burns)
            last_update = current_time
        lander_image = lander_burns[burn_frame]
    
    # Create a rotated lander image
    rot_lander = pygame.transform.rotate(lander_image, lander.rot)
    rot_lander_rect = rot_lander.get_rect(center=(lander.X + lander.width // 2, lander.Y + lander.height // 2))
    window.blit(rot_lander, rot_lander_rect)
    


    
def render_explosion(explosion_imgs, explosion_rot):

    global explosion_frame, last_explosion_update

    boundaries(lander, platforms)

    
    if current_time - last_explosion_update >= 200:
        explosion_frame = (explosion_frame + 1) % len(explosion_imgs)
        last_explosion_update = current_time
    explosion_image = explosion_imgs[explosion_frame]

    if explosion_rot == 0:
        explosion_Y = lander.Y
    if explosion_rot == 180:
        explosion_Y = lander.Y + lander.height
        
    platform_crash = touching()
    
    if platform_crash > 0:
        platform = platforms.index(platform_crash)
        if lander.X - lander.width // 2 < platform.X:
            lander.X = platform.X + lander.width // 0.5
        if lander.X + lander.width * 1.5 > platform.X + platform.width:
            lander.X = platform.X + platform.width - lander.width * 1.5
            
    # Draw explosion on window
    rot_explosion = pygame.transform.rotate(explosion_image, explosion_rot)
    rot_explosion_rect = rot_explosion.get_rect(center=(lander.X + lander.width // 2, explosion_Y))
    window.blit(rot_explosion, rot_explosion_rect)
    

    

lander_imgs = []
explosion_imgs = []

load_images(lander)
lander_img = lander_imgs[0]
lander_burns = [lander_imgs[1], lander_imgs[2]]


burn_frame = 0
explosion_frame = 0
last_update = pygame.time.get_ticks()
last_explosion_update = pygame.time.get_ticks()

explosion_rot = 0

boundaries(lander, platforms)

lander.X = platform_1.X + platform_1.width // 2 - lander.width // 2
lander.Y = platform_1.top - lander.height

# Game loop
alive = True
running = True
while running:

    # assign time
    current_time = pygame.time.get_ticks()
    
    # start keyboard
    keys = pygame.key.get_pressed()

    # check if window close
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False

    # check if respawn
    if keys[pygame.K_SPACE]:
            alive = True
            lander.X = platform_1.X + platform_1.width // 2 - lander.width // 2
            lander.Y = platform_1.top - lander.height
            lander.vel_x = 0
            lander.vel_y = 0
            lander.rot = 0

            
    # assign fps
    frame_rate = int(clock.get_fps())
    if frame_rate == 0:
        frame_rate = 120


    # game
    if alive:
        
        boundaries(lander, platforms)
        lander.physics_control()
        collision_detection(lander, platforms)
        window.fill(WHITE)
        render_platforms(platforms)
        render_lander(lander_img, lander_burns)
        text(WIDTH - 10, 40, 'up fastness', round(-lander.vel_y))
        text(WIDTH - 10, 80, 'turn', round(lander.rot))
        pygame.display.flip()
        
        
    else:
        
        window.fill(WHITE)
        render_platforms(platforms)
        text(WIDTH - 10, 40, 'up fastness', round(-lander.vel_y))
        text(WIDTH - 10, 80, 'turn', round(lander.rot))
        render_explosion(explosion_imgs, explosion_rot)
        pygame.display.flip()
        

            
    # Control the frame rate
    clock.tick(FPS)
    
# Quit the game
pygame.quit()
