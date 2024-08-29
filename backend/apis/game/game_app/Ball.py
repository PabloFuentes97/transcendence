from . import Player
import numpy as np
import math
import random

X = 0
Y = 1

LEFT = False
RIGHT = True

SCREEN_HEIGHT = Player.SCREEN_HEIGHT
SCREEN_WIDTH = Player.SCREEN_WIDTH

ACC_SPEED = 3000 * 10
OG_SPEED = 12000 * 10
TOP_SPEED = 36000 * 10

SIDE_LEN = 20

MAX_DEG = 60 # Maximo angulo de rebote
MIRROR_DEG = 180 - (2 * MAX_DEG) # Constante de correccion de espejo

class ball():

    def __init__(self):
        self.__side_len = SIDE_LEN
        self.__pos = [0 - self.__side_len/2, 0 + self.__side_len/2]
        self.__uni_dir = [ 1, 0]   # Empieza hacia la derecha siempre [1, 0]
        self.__serve = False       # Player that serves next
        self.__fixed = False
        self.__speed = OG_SPEED
        self.__base_speed = OG_SPEED

# GETTERS && SETTERS

    def get_pos(self):
        return self.__pos
    
    def get_dir(self):
        return self.__uni_dir
    
    def get_side_len(self):
        return self.__side_len
    
    def get_serve(self):
        return self.__serve
    
    def set_speed(self, speed):
        self.__speed = speed

    def get_speed(self):
        return self.__speed
    
    def set_base_speed(self, base_speed):
        self.__base_speed = base_speed

    def get_base_speed(self):
        return self.__base_speed

    def is_fixed(self):
        if (self.__fixed):
            self.__fixed = False
            return True
        return False
    
    def set_dir(self, dir: list):
        self.__uni_dir = dir

# Spawns a BALL at the center facing one player each time

    def spawn_random(self):
        self.__serve = not self.__serve
        self.__base_speed = OG_SPEED
        self.__pos[X] = 0 - self.__side_len/2
        self.__pos[Y] = random.randint(-50, 50) + self.__side_len/2
        random_angle = random.randint(-60, 60) + (180 * self.__serve)
        self.__uni_dir = [math.cos(math.radians(random_angle)),
                        math.sin(math.radians(random_angle))]

    def accelerate(self):
        if (self.__base_speed < TOP_SPEED):
            self.__base_speed = self.__base_speed + ACC_SPEED
        
        #print("ACCELERATE")

    def hit_wall(self):
        self.__uni_dir[Y] *= -1

    def overlap(self, player: Player.player):
        corners = [self.__pos,
                   [self.__pos[X] + self.__side_len, self.__pos[Y]],
                   [self.__pos[X], self.__pos[Y] + self.__side_len],
                   [self.__pos[X] + self.__side_len, self.__pos[Y] + self.__side_len]]
        #if ()
        for corner in corners:
            if (player.get_pos()[X] < corner[X] < player.get_pos()[X] + player.get_dim()[X]
                and player.get_pos()[Y] - player.get_dim()[Y] < corner[Y] < player.get_pos()[Y]):
                return True

        return False

    def fix_player_overlap(self, player: Player.player):

        if ((self.__pos[Y] - self.__side_len / 2) > (player.get_pos()[Y] - player.get_dim()[Y] / 2)):
            self.__pos[Y] = player.get_pos()[Y] + SIDE_LEN
        else:
            self.__pos[Y] = player.get_pos()[Y] - player.get_dim()[Y]
        if (self.__pos[Y] > SCREEN_HEIGHT/2):
            self.__pos[Y] = SCREEN_HEIGHT/2
        elif (self.__pos[Y] < -SCREEN_HEIGHT/2):
            self.__pos[Y] = -SCREEN_HEIGHT/2
        #self.__pos[X] = player.get_pos()[X] + player.get_dim()[X] if not player.get_side() else player.get_pos()[X] - self.__side_len
        self.set_dir(self.player_bounce_angle(player))
        self.accelerate()
        self.__fixed = True


# Check next ball to fix its position if it collides

    def check_collisions(self, player1: Player.player, player2: Player.player, game):
        pot_pos = [self.__pos[X] + (self.__uni_dir[X] * self.__speed * game.deltaTime),
                        self.__pos[Y] + (self.__uni_dir[Y] * self.__speed * game.deltaTime)]
        if((not self.is_fixed()) and self.player_hit(pot_pos, player1, player2)):
            game.flag = "player"
            return
        
        if(self.goal(game)):
            return

        if (self.wall_bounce(pot_pos)):
            game.flag = "wall"
            return

        self.__pos = pot_pos

    # CHECK PLAYER HIT - WIP
    def player_hit(self, pot_pos: list, player1: Player.player, player2: Player.player):
        #return False
        if (self.get_dir()[X] < 0 and pot_pos[X] <= (player1.get_pos()[X] + player1.get_dim()[X])):
            return (self.hit_player(player1, pot_pos))
        elif (self.get_dir()[X] > 0 and pot_pos[X] + self.__side_len >= player2.get_pos()[X]):
            return (self.hit_player(player2, pot_pos))
        return False
    
    def hit_player(self, player: Player.player, pot_pos: list):
        mov_vec = [pot_pos[X] - self.__pos[X], pot_pos[Y] - self.__pos[Y]]

        adj_pos = self.get_adj_pos(player, pot_pos, mov_vec)

        if (adj_pos):

            #print("------INIT POS =", self.__pos, "------")
            #print("------MOV VEC =", mov_vec, "------")
            #print("MAG =", np.linalg.norm(mov_vec))
            #print("------POTENTIAL POS =", pot_pos, "------")
            #print("------ADJ POS =", adj_pos, "------\n")

            self.__pos = adj_pos
            self.set_dir(self.player_bounce_angle(player))
            self.accelerate()

            return True

        return False

    def get_adj_pos(self, player: Player.player, pot_pos: list, mov_vec: list):
        adj_X = player.get_pos()[X] + ((player.get_dim()[X]) * (not player.get_side())) - self.__side_len * player.get_side()
        try:
            adj_Y = self.__pos[Y] + (((adj_X - self.__pos[X]) / mov_vec[X]) * mov_vec[Y])
        except:
            adj_Y = self.__pos[Y] + mov_vec[Y]
        
        # SIDE
        if (((self.__pos[X] + self.__side_len <= player.get_pos()[X]) if player.get_side()
             else (self.__pos[X] >= player.get_pos()[X] + player.get_dim()[X]))
            and self.check_inside_range([adj_Y, adj_Y - self.__side_len]
                                , [player.get_pos()[Y], player.get_pos()[Y] - player.get_dim()[Y]])):
            #print ("PLAYER SIDE HIT")
            #print("------INIT POS =", self.__pos, "------")
            #print("------MOV VEC =", mov_vec, "------")
            #print("------POTENTIAL POS =", pot_pos, "------")
            #print("------PLAYER POS =", player.get_pos(), "------")
            #print("------PLAYER BOT =", player.get_pos()[Y] - player.get_dim()[Y], "------")
            
            return [adj_X, adj_Y]
        
        # TOP
        elif (self.__pos[Y] - self.__side_len >= player.get_pos()[Y]
              and pot_pos[Y] - self.__side_len <= player.get_pos()[Y]):
            adj_Y = player.get_pos()[Y] + self.__side_len
            try :
                adj_X = self.__pos[X] + (((adj_Y - self.__pos[Y]) / mov_vec[Y]) * mov_vec[X])
            except ZeroDivisionError:
                adj_X = self.__pos[X] + mov_vec[X]
            #print ("TOP")
            
            if (self.check_inside_range([adj_X, adj_X + self.__side_len]
                                , [player.get_pos()[X] + player.get_dim()[X], player.get_pos()[X]])):
                #print("------INIT POS =", self.__pos, "------")
                #print("------MOV VEC =", mov_vec, "------")
                #print("------POTENTIAL POS =", pot_pos, "------")
                #print("------PLAYER POS =", player.get_pos(), "------")
                #print("------PLAYER BOT =", player.get_pos()[Y] - player.get_dim()[Y], "------")
                #print ("ADJ_POS =", adj_X, adj_Y)
                #print ("ADJ_RANGE =", adj_X, adj_X + self.__side_len)
                #print ("PLAYER RANGE =", player.get_pos()[X] + player.get_dim()[X], player.get_pos()[X])
                #print ("PLAYER TOP HIT")
                return [adj_X, adj_Y]
        # BOT
        elif (self.__pos[Y] <= player.get_pos()[Y] - player.get_dim()[Y]
              and pot_pos[Y] >= player.get_pos()[Y] - player.get_dim()[Y]):
            adj_Y = player.get_pos()[Y] - player.get_dim()[Y]
            try :
                adj_X = self.__pos[X] + (((adj_Y - self.__pos[Y]) / mov_vec[Y]) * mov_vec[X])
            except ZeroDivisionError:
                adj_X = self.__pos[X] + mov_vec[X]
            #print ("BOT")
            
            if (self.check_inside_range([adj_X, adj_X + self.__side_len]
                                , [player.get_pos()[X] + player.get_dim()[X], player.get_pos()[X]])):
                #print("------INIT POS =", self.__pos, "------")
                #print("------MOV VEC =", mov_vec, "------")
                #print("------POTENTIAL POS =", pot_pos, "------")
                #print("------PLAYER POS =", player.get_pos(), "------")
                #print("------PLAYER BOT =", player.get_pos()[Y] - player.get_dim()[Y], "------")
                #print ("ADJ_POS =", adj_X, adj_Y)
                #print ("ADJ_RANGE =", adj_X, adj_X + self.__side_len)
                #print ("PLAYER RANGE =", player.get_pos()[X] + player.get_dim()[X], player.get_pos()[X])
                #print ("PLAYER BOT HIT")
                return [adj_X, adj_Y]

        #print ("NONE")
        return False
    
    def check_inside_range(self, points: list, range: list):
        if ((range[1] < points[0] < range[0])) or (range[1] < points[1] < range[0]):
            return True
        return False
    
    def player_bounce_angle(self, player: Player.player):
        dist = (player.get_pos()[Y] - player.get_dim()[Y]/2) - (self.__pos[Y] - self.__side_len/2)
        fixed_dist = max( - player.get_dim()[Y]/2, min(player.get_dim()[Y]/2, dist))
        angle = (MAX_DEG * fixed_dist/(player.get_dim()[Y]/2)) * -1
        mirror = 180 - (2 * angle)
        final_angle = angle + (mirror * player.get_side())
        return [math.cos(math.radians(final_angle)), math.sin(math.radians(final_angle))]


    # CHECK GOAL - DONE
    def goal(self, game):
        if ((self.__pos[X] + self.__side_len >= SCREEN_WIDTH/2)
            or (self.__pos[X] <= -SCREEN_WIDTH/2)):

            #print("\nGOLAAAAAASO!!!")
            #print("PLAYER 1\n" if self.__uni_dir[X] > 0 else "PLAYER 2\n")
            game.score(LEFT) if self.__uni_dir[X] > 0 else game.score(RIGHT)
            self.spawn_random()
            return True

        return False

    # CHECK WALL BOUNCE - DONE
    def wall_bounce(self, pot_pos: list):
        if ((pot_pos[Y] >= SCREEN_HEIGHT/2) or
            ((pot_pos[Y] - self.__side_len) <= -(SCREEN_HEIGHT/2))):
        
            nearest_point = [max(-(SCREEN_WIDTH/2), min((SCREEN_WIDTH/2), pot_pos[X]))
                            , SCREEN_HEIGHT/2 if self.__uni_dir[Y] > 0 else -SCREEN_HEIGHT/2]

            ray_to_nearest = [nearest_point[X] - pot_pos[X],
                              nearest_point[Y] - pot_pos[Y]]

            magnitude = np.linalg.norm(ray_to_nearest)

            overlap = self.__side_len - magnitude

            if (overlap > 0):
                #print ("WALL HIT")
                try:
                    self.__pos[X] = pot_pos[X] - ((ray_to_nearest[X] / magnitude) * overlap)
                    self.__pos[Y] = pot_pos[Y] - (((ray_to_nearest[Y] / magnitude) * overlap)) - (0 if self.__uni_dir[Y] < 0 else self.__side_len)
                except ZeroDivisionError:
                    self.__pos[X] = pot_pos[X] - overlap
                    self.__pos[Y] = pot_pos[Y] - overlap - (0 if self.__uni_dir[Y] < 0 else self.__side_len)
                self.hit_wall()
                #print("\n------FINAL POS =", self.__pos, "------\n")
                return True

        return False