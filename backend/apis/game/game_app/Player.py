X = 0
Y = 1

SCREEN_HEIGHT = 500
SCREEN_WIDTH = 800

PLAYER_DIST_TO_LIMITS = 30

PLAYER_WIDTH = 20
PLAYER_HEIGHT = 80

BASE_SPEED = 600 * 2.2

LEFT = False
RIGHT = True

class player():

    # Poner en su lado segun side
    # y a mitad de la altura total

    def __init__(self, side: bool):
        self.__side = side
        self.__pos = self.set_side(side) # top left position
        self.__mov = False
        self.__dim = [PLAYER_WIDTH, PLAYER_HEIGHT]
        self.__speed = BASE_SPEED

    def get_pos(self):
        return self.__pos

    def get_dim(self):
        return self.__dim
    
    def get_side(self):
        return self.__side
    
    def get_mov(self):
        return self.__mov
    
    def set_speed(self, speed):
        self.__speed = speed
    
    def set_side(self, side: bool):
        if (not side):
            return [-((SCREEN_WIDTH / 2) - PLAYER_DIST_TO_LIMITS), PLAYER_HEIGHT/2]
        else:
            return [((SCREEN_WIDTH / 2) - (PLAYER_DIST_TO_LIMITS + PLAYER_WIDTH)), PLAYER_HEIGHT/2]
        
    def move(self, input, ball):
        if (not input):
            return
        self.__pos[Y] += self.__speed if input == "UP" else -self.__speed
        if (self.__pos[Y] < -SCREEN_HEIGHT/2 + PLAYER_HEIGHT):
            self.__pos[Y] = -SCREEN_HEIGHT/2 + PLAYER_HEIGHT
        elif (self.__pos[Y] > SCREEN_HEIGHT/2):
            self.__pos[Y] = SCREEN_HEIGHT/2
        if (((ball.get_dir()[X] < 0) if not self.__side else (ball.get_dir()[X] > 0))
            and ball.overlap(self)):
            ball.fix_player_overlap(self)

    def set_vertical_pos(self, newPosY, ball):
        if (newPosY + PLAYER_HEIGHT/2 == self.__pos[Y]):
            return
        self.__pos[Y] = newPosY + PLAYER_HEIGHT/2
        if (self.__pos[Y] < -SCREEN_HEIGHT/2 + PLAYER_HEIGHT):
            self.__pos[Y] = -SCREEN_HEIGHT/2 + PLAYER_HEIGHT
        elif (self.__pos[Y] > SCREEN_HEIGHT/2):
            self.__pos[Y] = SCREEN_HEIGHT/2
        if (((ball.get_dir()[X] < 0) if not self.__side else (ball.get_dir()[X] > 0))
            and ball.overlap(self)):
            ball.fix_player_overlap(self)


    def set_move(self, input: str):
        self.__mov = input

    def set_move_up(self):
        self.__mov = "UP"
    
    def set_move_down(self):
        self.__mov = "DOWN"
    
    def set_move_false(self):
        self.__mov = False