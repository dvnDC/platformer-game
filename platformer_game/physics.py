from pygame.math import Vector2


class Physics(object):
    def __init__(self, game):
        self.game = game
        self.gravity = 0.9

        self.pos = Vector2(300, 170)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.width = 20
        self.height = 60
        self.true_scroll = [0, 0]
        self.true_scroll2 = [0, 0]
        self.isStanding = False

    def standing(self):
        self.game.collision.enemy_collision()
        self.isStanding = self.game.collision.isBottomCollision

    def set_scroll(self, scroll):
        game_objects = [self.game.map, self.game.player, self.game.platforms,
                        self.game.enemy, self.game.fire, self.game.collision,
                        self.game.weapon]

        for obj in game_objects:
            obj.scroll.x = scroll[0]
            obj.scroll.y = scroll[1]

    def scroll(self):
        self.true_scroll[0] += (self.game.player.pos.x - self.true_scroll[0] - 640) / 40
        self.true_scroll[1] += (self.game.player.pos.y - self.true_scroll[1] - 170)
        scroll = [int(x) for x in self.true_scroll]

        self.set_scroll(scroll)

        self.game.platforms.true_scroll.x = self.true_scroll2[0]  # To be removed

    def tick(self):
        self.scroll()
        # self.standing()