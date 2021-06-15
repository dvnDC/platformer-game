from pygame.math import Vector2


class Physics(object):

    def __init__(self, game):
        self.game = game
        self.gravity = 0.9

        self.pos = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.pos.x = 300
        self.pos.y = 170
        self.width = 20
        self.height = 60

        self.position = (0, 0, 0, 0)  # x0 x1 y0 y1

        self.true_scroll = [0,0]
        self.true_scroll2 = [0,0]



        self.isStanding = False

    def standing(self):
        self.game.collision.enemy_collision()
        if self.game.collision.isBottomCollision == True:
            self.isStanding = True
        else:
            self.isStanding = False

    def scroll(self):
        #################33
        self.true_scroll[0] += (self.game.player.pos.x - self.true_scroll[0] - 640)/40
        ###
        # self.true_scroll2[0] += (self.game.player.pos.x - self.true_scroll[0]-640)
        self.true_scroll[1] += (self.game.player.pos.y - self.true_scroll[1] - 170)
        scroll = self.true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        self.game.map.scroll.x = scroll[0]
        self.game.map.scroll.y = scroll[1]
        self.game.player.scroll.x = scroll[0]
        self.game.player.scroll.y = scroll[1]
        self.game.scroll.x = scroll[0]
        self.game.scroll.y = scroll[1]
        self.game.platforms.scroll.x = scroll[0]
        self.game.platforms.scroll.y = scroll[1]
        self.game.enemy.scroll.x = scroll[0]
        self.game.enemy.scroll.y = scroll[1]
        self.game.fire.scroll.x = scroll[0]
        self.game.fire.scroll.y = scroll[1]
        self.game.collision.scroll.x = scroll[0]
        self.game.collision.scroll.y = scroll[1]
        self.game.weapon.scroll.x = scroll[0]
        self.game.weapon.scroll.y = scroll[1]

        self.game.platforms.true_scroll.x = self.true_scroll2[0] #DO WYRZUCENIA


    def tick(self):

        self.scroll()

