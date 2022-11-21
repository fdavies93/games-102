import pygame
import time

class FpsCounter():
    
    def __init__(self):
        self.frames = 0
        self.prev_render = 0
        self.prev_frames = 0
        self.font = pygame.font.Font(None, 24)
    
    def render(self, surface : pygame.Surface, position : pygame.rect.Rect):
        if time.time() > self.prev_render + 0.25:
            self.prev_frames = (self.frames * 4)
            self.frames = 0
            self.prev_render = time.time()

        self.frames += 1
        font_surface = self.font.render(f"FPS: {str(self.prev_frames)}", True, (255,255,255))
        surface.blit(font_surface, position)