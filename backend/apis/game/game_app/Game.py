from . import Ball
from . import Player
import time

MAX_FPS = 180
MIN_FPS = 180

LOW_LIMIT = 1000 / MAX_FPS / 1000
HIGH_LIMIT = 1000 / MIN_FPS / 1000

X = 0
Y = 1

LEFT = False
RIGHT = True

SCREEN_HEIGHT = Player.SCREEN_HEIGHT
SCREEN_WIDTH = Player.SCREEN_WIDTH

TIMELIMIT = 120

#INPUTS UP / DOWN / False

class game():

    def __init__(self):
        self.left_player = Player.player(LEFT)
        self.right_player = Player.player(RIGHT)
        self.ball = Ball.ball()
        self.scoreboard = [ 0, 0]
        self.flag = True
        self.state = "init"

        self.time = TIMELIMIT
        self.initTime = time.time()
        self.currTime = False
        self.lastTime = False
        self.waitDelay = 0
        self.totalWaitDelay = 0
        self.deltaTime = HIGH_LIMIT

        self.goalWaitInitTime = False
        self.goalWaitCurrTime = False

        """ self.frame = 0
        self.lag = 0 """

    def score(self, side: bool):
        
        if (self.state == "golden goal"):
            self.state = "ended"
        else:
            self.state = "waiting"
            self.goalWaitInitTime = time.time()
        #print ("Waiting...")
        if (side == LEFT):
            self.scoreboard[0] += 1
            self.flag = "left scored"
        elif (side == RIGHT):
            self.scoreboard[1] += 1
            self.flag = "right scored"

    def checkWaitTime(self):

        self.goalWaitCurrTime = time.time()
        
        self.waitDelay = self.goalWaitCurrTime - self.goalWaitInitTime

        if (self.goalWaitCurrTime > self.goalWaitInitTime + 3):
            
            self.totalWaitDelay += self.waitDelay
            self.waitDelay = 0
            self.goalWaitInitTime = False
            self.state = "playing"
            return True
        
        return False

    def updateState(self):

        if (self.state != "waiting" and self.currTime - self.initTime >= TIMELIMIT ):

            if (self.scoreboard[0] != self.scoreboard[1]):
                self.state = "ended"
                #print("END OF GAME")
                #print("Score", self.scoreboard[0], " - ", self.scoreboard[1])

            else:
                self.state = "golden goal"
                #print("GOLDEN GOAL")


    # Gets players inputs and returns BALL_POSITION and PLAYERS_POSITION
    def update_frame(self, input1, input2):
        
        if (self.state == "init"):
            self.state = "playing"
            self.initTime = time.time()
            self.currTime = time.time()
        
        self.lastTime = self.currTime

        self.currTime = time.time() - self.waitDelay - self.totalWaitDelay

        #print ("LAST TIME =", self.lastTime)
        #print ("CURR TIME =", self.currTime)

        self.deltaTime = (self.currTime - self.lastTime) #* 1000

        #print("PRE FIX DELTA TIME=", self.deltaTime)

        if self.deltaTime < LOW_LIMIT:
            #print ("LOW LIMIT DELTA")
            self.deltaTime = LOW_LIMIT
        elif self.deltaTime > HIGH_LIMIT:
            #print ("HIGH LIMIT DELTA")
            self.deltaTime = HIGH_LIMIT

        #print("DELTA TIME=", self.deltaTime)

        self.ball.set_speed(self.ball.get_base_speed() * self.deltaTime)

        self.right_player.set_speed(Player.BASE_SPEED * self.deltaTime)
        self.left_player.set_speed(Player.BASE_SPEED * self.deltaTime)

        #print("PLAYER SPEED POST= ", Player.speed)

        self.updateState()

        self.flag = False
        
        self.left_player.move(input1, self.ball)
        self.right_player.move(input2, self.ball)

        if (self.state == "golden goal"):
            self.time = -1
        else:
            self.time = (TIMELIMIT - (self.currTime - self.initTime)) if (TIMELIMIT - (self.currTime - self.initTime)) > 0 else 0
        
        if (self.goalWaitInitTime != False and not self.checkWaitTime()):
            return

        self.ball.check_collisions(self.left_player, self.right_player, self)

    def get_frame_info(self):

        return ({"Ball":[self.ball.get_pos()[X] + Ball.SIDE_LEN/2, self.ball.get_pos()[Y] - Ball.SIDE_LEN/2]
                , "Left_Player":[self.left_player.get_pos()[X] + Player.PLAYER_WIDTH/2, self.left_player.get_pos()[Y] - Player.PLAYER_HEIGHT/2]
                , "Right_Player":[self.right_player.get_pos()[X] + Player.PLAYER_WIDTH/2, self.right_player.get_pos()[Y] - Player.PLAYER_HEIGHT/2]
                , "Score":self.scoreboard, "Hit":self.flag, "State": self.state
                , "Time": self.time}) #Flag: False, "player", "wall" or "goal"
