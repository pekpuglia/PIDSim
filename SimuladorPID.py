import pygame
import Vetores

pygame.init()
scrw, scrh = 1100, 600
screen = pygame.display.set_mode([scrw, scrh])
kg = True
timer = pygame.time.Clock()
font = pygame.font.SysFont("sourcecodeproblack", 12)


def constrain(a, min, max):
    return max if a >= max else min if a <= min else a


class Slider:
    # poder digitar max, min, valor ( e mudar posicao do botao nos casos certos )
    def __init__(self, pos, bgcolor, max, min, name):
        self.rect = pygame.Rect(100*pos, 0, 100, scrh)
        self.bgcolor = bgcolor
        self.slider_rail = pygame.Rect(100*pos+55, 50, 10, scrh - 2*50)
        self.button_w = 20
        self.button_h = 10
        self.button_rect = pygame.Rect(self.slider_rail.centerx - self.button_w/2,
                                       self.slider_rail.bottom - self.button_h/2, self.button_w, self.button_h)
        self.max = max
        self.min = min
        self.grabbed = False
        self.name = name
        self.edit = 0  # 1 é upper, 2 é middle e 3 é lower

    def get_value(self):
        return self.min + (self.button_rect.centery - self.slider_rail.bottom) * (self.max - self.min)/(self.slider_rail.top - self.slider_rail.bottom)

    def set_value(self, value):
        value = constrain(value, self.min, self.max)
        self.button_rect.centery = self.slider_rail.top + \
            (value - self.max) * (self.slider_rail.bottom -
                                  self.slider_rail.top)/(self.min - self.max)

    def write(self, text):
        name_text = font.render(self.name, True, (0, 0, 0))
        name_text_rect = name_text.get_rect()
        name_text_rect.centerx = self.rect.centerx
        name_text_rect.y = 5
        screen.blit(name_text, name_text_rect)
        cores = []
        for x in [1, 2, 3]:
            cores.append((255, 255, 255) if self.edit == x else (0, 0, 0))

        upper_string = f"{text if self.edit == 1 else self.max}"
        upper_text = font.render(
            upper_string, True, cores[0])
        upper_text_rect = upper_text.get_rect()
        upper_text_rect.centerx = self.slider_rail.centerx
        upper_text_rect.centery = self.slider_rail.top - \
            (upper_text_rect.height)
        self.upper_text_rect = upper_text_rect
        screen.blit(upper_text, upper_text_rect)

        middle_string = f"{text if self.edit == 2 else self.get_value():.2f}"
        middle_text = font.render(
            middle_string, True, cores[1])
        middle_text_rect = middle_text.get_rect()
        middle_text_rect.centerx = self.slider_rail.x - middle_text_rect.width/2 - 5
        middle_text_rect.centery = self.slider_rail.centery
        self.middle_text_rect = middle_text_rect

        lower_string = f"{text if self.edit == 3 else self.min}"
        lower_text = font.render(
            lower_string, True, cores[2])
        lower_text_rect = lower_text.get_rect()
        lower_text_rect.centerx = self.slider_rail.centerx
        lower_text_rect.centery = self.slider_rail.bottom + 15
        self.lower_text_rect = lower_text_rect
        screen.blit(lower_text, lower_text_rect)

        screen.blit(middle_text, middle_text_rect)

    def update(self, pos, text):
        if self.grabbed:
            # limita o button no rail e muda pos do button de acordo com mouse
            if self.slider_rail.top <= pos[1] <= self.slider_rail.bottom:
                self.button_rect.centery = pos[1]
            elif pos[1] < self.slider_rail.top:
                self.button_rect.centery = self.slider_rail.top
            elif pos[1] > self.slider_rail.bottom:
                self.button_rect.centery = self.slider_rail.bottom
        # desenha o plano de fundo
        pygame.draw.rect(screen, self.bgcolor, self.rect)
        # slider rail
        pygame.draw.rect(screen, (50, 50, 50), self.slider_rail)
        # button
        pygame.draw.rect(screen, (200, 200, 200), self.button_rect)

        self.write(text)


class LineFollower:
    def __init__(self):
        # fazer pausa
        self.line = scrh/2
        self.height = scrh/2 - 100
        self.displacement = self.height - self.line  # proporcional
        self.hor_speed = 5
        self.vert_speed = 0  # diferencial
        self.vert_acc = 0
        self.integral = 0  # p controle integral
        self.x = int((300+scrw)/2)
        # lista dos pontos anteriores para visuazilação
        # a bolinha em si não se move
        self.old_points_h = []
        # posições horizontais, não é alterada
        self.old_points_x = [300 + self.hor_speed *
                             t for t in range(int((scrw-300)/2/self.hor_speed))]

    def update(self, p, i, d):
        self.old_points_h.append(self.height)
        if len(self.old_points_h) > len(self.old_points_x):
            self.old_points_h.pop(0)
        self.vert_acc = - (p*self.displacement + i *
                           self.integral + d*self.vert_speed) / 1000
        self.vert_speed += self.vert_acc
        self.height += self.vert_speed
        self.displacement = self.height - self.line
        self.integral += self.displacement/100

    def render(self):
        # mostrar valores do PID
        pygame.draw.line(screen, (255, 255, 255), [
                         300, self.line], [scrw, self.line])
        pygame.draw.circle(screen, (150, 0, 200), [
                           self.x, int(self.height)], 10)
        for y, x in zip(self.old_points_h[::-1], self.old_points_x[::-1]):
            # listas invertidas p considerar casos em que self.old_points_h ainda
            # não foi completamente preenchida
            pygame.draw.circle(screen, (0, 200, 150), [int(x), int(y)], 2)


prop = Slider(0, (255, 0, 0), 100, 0, "Proporcional")
integral = Slider(1, (0, 255, 0), 0.1, 0, "Integral")
difer = Slider(2, (0, 0, 255), 100, 0, "Diferencial")
sliders = [prop, integral, difer]
a = LineFollower()
txt = ""
while kg:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            kg = False
        if ev.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            editing = 0
            new_edit = 0
            for slider in sliders:
                if slider.edit:
                    editing = slider
                    break
            for slider in sliders:
                if slider.slider_rail.collidepoint(pos):
                    slider.grabbed = True
                if slider.upper_text_rect.collidepoint(pos):
                    new_edit = slider
                    slider.edit = 1
                    txt = str(slider.max)
                if slider.middle_text_rect.collidepoint(pos):
                    new_edit = slider
                    slider.edit = 2
                    txt = str(slider.get_value())
                if slider.lower_text_rect.collidepoint(pos):
                    new_edit = slider
                    slider.edit = 3
                    txt = str(slider.min)
            if new_edit:
                try:
                    editing.edit = 0
                except AttributeError:
                    pass
        if ev.type == pygame.KEYDOWN:
            for slider in sliders:
                if slider.edit:
                    if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                        txt = txt.replace(",", ".")
                        for slider in sliders:
                            if slider.edit:
                                if slider.edit == 1:
                                    slider.max = float(txt)
                                elif slider.edit == 2:
                                    slider.set_value(float(txt))
                                elif slider.edit == 3:
                                    slider.min = float(txt)
                                slider.edit = 0
                        txt = ""
                    elif ev.key == pygame.K_BACKSPACE:
                        txt = txt[:-1]
                    else:
                        txt += ev.unicode
        if ev.type == pygame.MOUSEBUTTONUP:
            for slider in sliders:
                slider.grabbed = False
    screen.fill((0, 0, 0))
    pos = pygame.mouse.get_pos()
    for slider in sliders:
        slider.update(pos, txt)
    a.update(prop.get_value(), integral.get_value(), difer.get_value())
    a.render()
    pygame.display.update()
    timer.tick(60)
pygame.quit()
