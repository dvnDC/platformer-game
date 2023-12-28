from pygame.math import Vector2


class Collision(object):
    def __init__(self, game):
        self.game = game
        self.speed = 1

        self.pos = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.pos.x = 0
        self.pos.y = 0
        self.wide = 0
        self.height = 0
        self.scroll = Vector2(0, 0)

        self.position = self.game.player.position
        self.window_position = (0, self.game.screen_width, 0, self.game.screen_height)

        self.collisionMargin = 12

        self.isCollision = False
        self.isCollisionEnemy = False
        self.isCollisionGrid = False

        self.isRightCollision = False
        self.isLeftCollision = False
        self.isTopCollision = False
        self.isBottomCollision = False

        self.isBottom_RightCollision = False
        self.isBottom_LeftCollision = False

    def collision(self, xxyy, xxyy1):
        if xxyy[1] >= xxyy1[0] and xxyy[0] < xxyy1[1]:
            if xxyy[3] >= xxyy1[2] and xxyy[2] < xxyy1[3]:
                self.isCollision = True
        else:
            self.isCollision = False

    def collision_enemy(self, xxyy, xxyy1):
        if xxyy[1] >= xxyy1[0] and xxyy[0] < xxyy1[1]:
            if xxyy[3] >= xxyy1[2] and xxyy[2] < xxyy1[3]:
                self.isCollisionEnemy = True

    def collision_grid(self, xxyy, xxyy1):
        if xxyy[1] >= xxyy1[0] and xxyy[0] < xxyy1[1]:
            if xxyy[3] >= xxyy1[2] and xxyy[2] < xxyy1[3]:
                self.isCollisionGrid = True
        else:
            self.isCollisionGrid = False

    def collision_side(self, xxyy, xxyy1):
        if abs(xxyy[3] - xxyy1[2]) <= self.collisionMargin:
            self.isBottomCollision = True
        elif abs(xxyy[2] - xxyy1[3]) <= self.collisionMargin:
            self.isTopCollision = True

        if abs(xxyy[1] - xxyy1[0]) <= self.collisionMargin:
            self.isRightCollision = True
        elif abs(xxyy[0] - xxyy1[1]) <= self.collisionMargin:
            self.isLeftCollision = True

        if self.isBottomCollision == True and self.isRightCollision == True:
            self.isBottom_RightCollision = True
        if self.isBottomCollision == True and self.isLeftCollision == True:
            self.isBottom_LeftCollision = True

    def player_collision_check(self, object_rect_position):
        self.vel = self.game.player.vel
        self.position = self.game.player.position
        self.pos.x = self.game.player.pos.x
        self.pos.y = self.game.player.pos.y

        # Collision check
        self.collision_grid((self.position), (object_rect_position))
        if self.isCollisionGrid:
            self.collision_side((self.position), (object_rect_position))

            if self.isBottomCollision:
                self.pos.y -= self.vel.y
                self.vel.y = 0
            if self.isTopCollision:
                self.pos.y += self.vel.y + 5
                self.vel.y = 0.1
            if self.isRightCollision:
                if not self.isBottom_RightCollision:
                    self.pos.x -= self.vel.x + 4
                    self.vel.x *= 0.1
                else:
                    self.pos.y -= self.vel.y
                    self.vel.y = 0
            if self.isLeftCollision:
                if not self.isBottom_LeftCollision:
                    self.pos.x += self.vel.x + 4
                    self.vel.x *= 0.1
                else:
                    self.pos.y -= self.vel.y
                    self.vel.y = 0

        self.isBottomCollision = False
        self.isTopCollision = False
        self.isRightCollision = False
        self.isLeftCollision = False
        self.isBottom_RightCollision = False
        self.isBottom_LeftCollision = False
        self.isCollisionGrid = False

        # Update data
        self.game.player.vel = self.vel
        self.game.player.pos.x = self.pos.x
        self.game.player.pos.y = self.pos.y

    def object_collision_check(self, posx, width, posy, height, vel, object_rect_position):
        self.vel = vel
        self.position = posx, width, posy, height,
        self.pos.x = posx
        self.pos.y = posy

        # Collision check
        self.collision_grid((self.position), (object_rect_position))
        if self.isCollisionGrid:
            self.collision_side((self.position), (object_rect_position))

            if self.isBottomCollision:
                self.pos.y -= self.vel.y
                self.vel.y = 0
            if self.isTopCollision:
                self.pos.y += self.vel.y + 5
                self.vel.y = 0.1
            if self.isRightCollision:
                if not self.isBottom_RightCollision:
                    self.pos.x -= self.vel.x + 4
                    self.vel.x *= 0.1
                else:
                    self.pos.y -= self.vel.y
                    self.vel.y = 0
            if self.isLeftCollision:
                if not self.isBottom_LeftCollision:
                    self.pos.x += self.vel.x + 4
                    self.vel.x *= 0.1
                else:
                    self.pos.y -= self.vel.y
                    self.vel.y = 0

        self.isBottomCollision = False
        self.isTopCollision = False
        self.isRightCollision = False
        self.isLeftCollision = False
        self.isBottom_RightCollision = False
        self.isBottom_LeftCollision = False
        self.isCollisionGrid = False

        return self.pos.x, self.pos.y, self.vel

    def player_collision(self):  # platforms, borders
        self.vel = self.game.player.vel
        self.position = self.game.player.position
        self.pos.x = self.game.player.pos.x
        self.pos.y = self.game.player.pos.y

        n = 3
        k = 0
        # Collision with platforms
        while n > 0:
            n -= 1
            self.collision((self.position), (self.game.platforms.platform_positions[k]))
            if self.isCollision:
                self.collision_side((self.position), (self.game.platforms.platform_positions[k]))

                if self.isBottomCollision:
                    self.pos.y -= self.vel.y
                    self.vel.y = 0
                if self.isTopCollision:
                    self.pos.y += self.vel.y + 5
                    self.vel.y = 0.1
                if self.isRightCollision:
                    if not self.isBottom_RightCollision:
                        self.pos.x -= self.vel.x + 4
                        self.vel.x *= 0.1
                    else:
                        self.pos.y -= self.vel.y
                        self.vel.y = 0
                if self.isLeftCollision:
                    if not self.isBottom_LeftCollision:
                        self.pos.x += self.vel.x + 4
                        self.vel.x *= 0.1
                    else:
                        self.pos.y -= self.vel.y
                        self.vel.y = 0
            k += 1

        self.isBottomCollision = False
        self.isTopCollision = False
        self.isRightCollision = False
        self.isLeftCollision = False

        self.game.player.vel = self.vel
        self.game.player.pos.x = self.pos.x
        self.game.player.pos.y = self.pos.y

    def player_enemy_collision(self):
        self.vel = self.game.player.vel
        self.position = self.game.player.position
        self.pos.x = self.game.player.pos.x
        self.pos.y = self.game.player.pos.y

        # Collision with enemy
        self.collision((self.position), (self.game.enemy.position))
        if self.isCollision:
            # self.pos.x = self.pos.x + self.vel.x - 10
            # self.pos.y -= 10
            self.collision_side((self.position), (self.game.enemy.position))

        if self.isBottomCollision:
            self.pos.y -= self.vel.y
            self.vel.y = 0
        if self.isTopCollision:
            self.pos.y += self.vel.y + 5
            self.vel.y = 0.1
        if self.isRightCollision:
            if not self.isBottom_RightCollision:
                # self.pos.x -= self.vel.x + 4
                # self.vel.x *= 0.1
                self.pos.x = self.pos.x + self.vel.x - 10
                self.pos.y -= 8
            else:
                self.pos.y -= self.vel.y + 2
                # self.vel.y = 0
        if self.isLeftCollision:
            if not self.isBottom_LeftCollision:
                self.pos.x = self.pos.x + self.vel.x + 10
                self.pos.y -= 8
            else:
                self.pos.y -= self.vel.y + 2
                # self.vel.y = 0

        # Update data
        self.game.player.vel = self.vel
        self.game.player.pos.x = self.pos.x
        self.game.player.pos.y = self.pos.y

    def bullet_collision(self):
        # enemy
        if self.game.enemy.pos.x - 50 <= self.game.fire.pos.x <= self.game.enemy.pos.x + 50:
            if self.game.enemy.pos.y - 20 <= self.game.fire.pos.y <= self.game.enemy.pos.y + 60:
                self.game.enemy.live = False

    def enemy_collision(self):
        self.vel = self.game.enemy.vel
        self.pos.x = self.game.enemy.pos.x
        self.pos.y = self.game.enemy.pos.y
        self.position = self.game.enemy.position

        # Update data
        self.game.enemy.vel = self.vel
        self.game.enemy.position = self.position
        self.game.enemy.pos.x = self.pos.x
        self.game.enemy.pos.y = self.pos.y
