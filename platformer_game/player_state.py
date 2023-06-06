class PlayerState:
    def __init__(self):
        self.isJump = False
        self.isAttacking = False
        self.isRunning = False
        self.got_weapon = False
        self.runCount = 0