import cocos
import cocos.collision_model
import cocos.euclid
from pyglet import clock
from math import *
from pyglet.gl import *


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


class Layer(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super().__init__()
        self.__items = []
        self.collision_manager = cocos.collision_model.CollisionManagerBruteForce()

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
            self.collision_manager.add(item)
        
        for item in self.__items:
            for other in self.collision_manager.iter_colliding(item):
                item.on_collision(other)

    def add(self, item):
        super().add(item)
        self.__items.append(item)
        item.layer = self

    def remove(self, item):
        super().remove(item)
        self.__items.remove(item)


class Sprite(cocos.sprite.Sprite):
    def __init__(self,
                 image,
                 position=(0, 0),
                 scale=1.,
                 anchor=(0, 0),
                 collision_radius=None):

        super().__init__(image, position=position, scale=scale, anchor=anchor)

        self.layer = None

        if collision_radius is None:
            collision_radius = max(self.get_rect().size) / 2

        self.collision_radius = collision_radius
        self.cshape = cocos.collision_model.CircleShape(
            self.position, collision_radius)
        self.__destroy = False

    def update(self, dt):
        if self.__destroy:
            self.layer.remove(self)

        self.cshape.center = cocos.euclid.Vector2(*self.position)

    def on_collision(self, other):
        pass

    def __draw_circle(self, radius, position):
        if not Game.draw_debug:
            return
        verts = []
        nbr_points = 32
        for i in range(nbr_points):
            angle = radians(float(i) / nbr_points * 360.0)
            x = radius * cos(angle) + position[0]
            y = radius * sin(angle) + position[1]
            verts += [x, y]

        circle = pyglet.graphics.vertex_list(nbr_points, ('v2f', verts))
        glColor3f(0, 1, 0)
        circle.draw(GL_LINE_LOOP)

    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        pass

    def draw(self):
        super().draw()
        self.__draw_circle(self.collision_radius, self.cshape.center)

    def destroy(self):
        self.__destroy = True

class AnimatedSprite(Sprite):

    def __init__(self,
            animation,
            position=(0, 0),
            scale=1.,
            anchor=(0, 0),
            collision_radius=None):

        animation = pyglet.image.load_animation(animation)
        super().__init__(animation, position=position, scale=scale, anchor=anchor)