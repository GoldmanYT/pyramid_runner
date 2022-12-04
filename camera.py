class Camera:
    def __init__(self, level_w, level_h, w, h):
        self.level_w, self.level_h, self.w, self.h = level_w - w, level_h - h, w, h

    def pos(self, x, y):
        return max(-self.level_w, min(0, self.w // 2 - x)), max(-self.level_h, min(0, self.h // 2 - y))
