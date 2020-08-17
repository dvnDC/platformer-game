class Physics(object):

    def __init__(self, game):
        self.game = game
        self.gravity = 0.9

        self.isStanding = False

    def standing(self):
        self.game.collision.enemy_collision()
        if self.game.collision.isBottomCollision == True:
            self.isStanding = True
        else:
            self.isStanding = False

