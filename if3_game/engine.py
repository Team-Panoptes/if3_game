import cocos
import cocos.collision_model
from cocos.text import Label
import cocos.euclid
from pyglet import clock
from math import *
from pyglet.gl import *
import pyglet
from pathlib import Path


def init(resolution=[], title='Game by Game02'):
    cocos.director.director.init(*resolution, title)


class Game(cocos.scene.Scene):

    draw_debug = False

    def __init__(self):
        super().__init__()
        self.__layers = []
        clock.schedule(self.update)

    @property
    def debug(self):
        return Game.draw_debug

    @debug.setter
    def debug(self, value):
        Game.draw_debug = value

    def run(self):
        cocos.director.director.run(self)

    def update(self, dt):
        for layer in self.__layers:
            layer.update(dt)

    def add(self, layer):
        super().add(layer)
        self.__layers.append(layer)
        layer.game = self

    def remove_all_layers(self):
        while self.__layers:
            layer = self.__layers.pop(0)
            self.remove(layer)


class Layer(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super().__init__()
        self.__items = []
        self.__texts = []
        self.collision_manager = cocos.collision_model.CollisionManagerBruteForce()
        self.game = None

    def on_key_press(self, key, modifiers):
        for item in self.__items:
            item.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        for item in self.__items:
            item.on_key_release(key, modifiers)

    def update(self, dt):
        for item in self.__items:
            item.update(dt)

        self.collision_manager.clear() # fast, no leaks even if changed cshapes
        for item in self.__items:
            try:
                item.compute_center()
            except AttributeError:
                pass
            self.collision_manager.add(item)

        for item in self.__items:
            for other in self.collision_manager.iter_colliding(item):
                item.on_collision(other)

    def add(self, item):
        super().add(item)
        if isinstance(item, Text):
            self.__texts.append(item)
        else:
            self.__items.append(item)
        item.layer = self

    def remove(self, item):
        super().remove(item)
        if isinstance(item, Text):
            self.__texts.remove(item)
        else:
            self.__items.remove(item)


class Sprite(cocos.sprite.Sprite):
    def __init__(self,
                 image,
                 position=(0, 0),
                 scale=1.,
                 anchor=(0, 0),
                 collision_shape="rectangle"):

        if image[-4:] == '.gif':
            image = pyglet.resource.animation(image)

        super().__init__(image, position=position, scale=scale, anchor=anchor)

        self.layer = None

        if isinstance(collision_shape, str):
            if collision_shape == "rectangle":
                width, height = self.get_rect().size
                self.cshape= cocos.collision_model.AARectShape(self.position, width/2, height/2)

            elif collision_shape == "circle":
                collision_radius = max(self.get_rect().size) / 2
                self.cshape = cocos.collision_model.CircleShape(
                    self.position, collision_radius)
        elif isinstance(collision_shape, cocos.collision_model.Cshape):
            self.cshape = collision_shape
        else:
            raise(TypeError(f'collision_shape parameters need to be "rectangle" or "circle" or a cocos.collision_model.Cshape type'))

        self.__destroy = False
        self.collision_shape = collision_shape

    def compute_center(self):
        center = self.position[0] - self.image_anchor[0], self.position[1] - self.image_anchor[1]
        width, height = self.get_rect().size
        center = center[0] + width/2, center[1] + height/2

        self.cshape.center = cocos.euclid.Vector2(*center)

    def update(self, dt):
        if self.__destroy:
            self.layer.remove(self)

    def on_collision(self, other):
        pass

    def __draw_circle(self):
        radius = max(self.get_rect().size) / 2
        verts = []
        nbr_points = 32
        for i in range(nbr_points):
            angle = radians(float(i) / nbr_points * 360.0)
            x = radius * cos(angle) + self.cshape.center[0]
            y = radius * sin(angle) + self.cshape.center[1]
            verts += [x, y]

        circle = pyglet.graphics.vertex_list(nbr_points, ('v2f', verts))
        glColor3f(0, 1, 0)
        circle.draw(GL_LINE_LOOP)

    def __draw_rectangle(self):
        verts = []

        c = self.cshape.center

        rx = self.cshape.rx
        ry = self.cshape.ry

        verts +=  c[0] - rx, c[1] + ry
        verts +=  c[0] + rx, c[1] + ry
        verts +=  c[0] + rx, c[1] - ry
        verts +=  c[0] - rx, c[1] - ry

        rectangle = pyglet.graphics.vertex_list(4, ('v2f', verts))

        glColor3f(0, 1, 0)
        rectangle.draw(GL_LINE_LOOP)

    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        pass

    def draw(self):
        super().draw()
        if Game.draw_debug:
            if self.collision_shape == 'circle':
                self.__draw_circle()
            elif self.collision_shape == 'rectangle':
                self.__draw_rectangle()

    def destroy(self):
        self.__destroy = True


class AnimatedSprite(Sprite):

    def __init__(self,
            animation,
            position=(0, 0),
            scale=1.,
            anchor=(0, 0),
            collision_radius=None):

        super().__init__(animation, position=position, scale=scale, anchor=anchor)


class Text(Label):

    def __init__(self, text, position=(0,0), anchor=None):
        self.layer = None
        if anchor == "center":
            anchor_x = "center"
            anchor_y = "center"
        elif anchor == "left":
            anchor_x = "left"
            anchor_y = "center"
        elif anchor == "right":
            anchor_x = "right"
            anchor_y = "center"
        elif anchor == "bottom":
            anchor_x = "center"
            anchor_y = "bottom"
        elif anchor == "top":
            anchor_x = "center"
            anchor_y = "top"
        elif isinstance(anchor, (list, tuple)):
            anchor_x = anchor[0]
            anchor_y = anchor[0]
        else:
            anchor_x = "left"
            anchor_y = "bottom"

        x, y = position

        super().__init__( text=text, x=x, y=y,
            anchor_x=anchor_x, anchor_y=anchor_y)
