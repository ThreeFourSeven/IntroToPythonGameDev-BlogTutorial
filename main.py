import os
import pygame
import random


def point_in_circle(px: int, py: int, cx: int, cy: int, radius: int):
    return abs(px - cx) < radius and abs(py - cy) < radius


def circle_circle_(circle_a: (int, int, int), circle_b: (int, int, int)):
    distance = (circle_a[0] - circle_b[0], circle_a[1] - circle_b[1])
    radius = circle_a[2] + circle_b[2]
    return distance[0] ** 2 + distance[1] ** 2 <= radius ** 2


def box_in_box(box_a: (int, int, int, int), box_b: (int, int, int, int)):
    collision_x = box_a[0] + box_a[2] >= box_b[0] and box_b[0] + box_b[2] >= box_a[0]
    collision_y = box_a[1] + box_a[3] >= box_b[3] and box_b[1] + box_b[3] >= box_a[1]
    return collision_x and collision_y


def circle_box(circle: (int, int, int), box: (int, int, int, int)):
    closest_x = max(min(circle[0], box[0] + box[2] // 2), box[0] - box[2] // 2)
    closest_y = max(min(circle[1], box[1] + box[3] // 2), box[1] - box[3] // 2)
    distance_x = circle[0] - closest_x
    distance_y = circle[1] - closest_y
    return distance_x ** 2 + distance_y ** 2 <= circle[2] ** 2


def point_in_box(px: int, py: int, box: (int, int, int, int)):
    return box_in_box((px, py, 0, 0), box)


class ComponentType:
    Shape_ = 0
    Controller_ = 1
    Label_ = 2
    Drift_ = 3
    JumpController_ = 4


class ShapeType:
    Circle_ = 10
    Box_ = 11


class Component:
    def __init__(self, component_type):
        self.component_type = component_type
        self.entity = None

    def update(self, game):
        pass

    def draw(self, game):
        pass


def _default_on_collide(shape_a, shape_b):
    pass


class Shape(Component):
    def __init__(self, shape, shape_size, color):
        super().__init__(ComponentType.Shape_)
        self.ignored_entities = set()
        self.shape = shape
        self.shape_size = shape_size
        self.on_collide = _default_on_collide
        self.color = color
        self.texture = None

    def ignore(self, entity):
        self.ignored_entities.add(entity.id)

    def colliding_with(self, other):
        if other.entity.id in self.ignored_entities:
            return
        if self.shape == ShapeType.Circle_:
            if other.shape == ShapeType.Circle_ and circle_circle_(
                    (self.entity.position[0], self.entity.position[1], self.entity.scale * self.shape_size[0]),
                    (other.entity.position[0], other.entity.position[1], other.entity.scale * other.shape_size[0])):
                self.on_collide(self.entity, other.entity)
            elif other.shape == ShapeType.Box_ and circle_box(
                    (self.entity.position[0], self.entity.position[1], self.entity.scale * self.shape_size[0]), (
                            other.entity.position[0], other.entity.position[1],
                            other.entity.scale * other.shape_size[0],
                            other.entity.scale * other.shape_size[1])):
                self.on_collide(self.entity, other.entity)
        elif self.shape == ShapeType.Box_:
            if other.shape == ShapeType.Circle_ and circle_box(
                    (other.entity.position[0], other.entity.position[1], other.entity.scale * other.shape_size[0]), (
                            self.entity.position[0], self.entity.position[1], self.entity.scale * self.shape_size[0],
                            self.entity.scale * self.shape_size[1])):
                self.on_collide(self.entity, other.entity)
            elif other.shape == ShapeType.Box_ and box_in_box((
                    self.entity.position[0], self.entity.position[1], self.entity.scale * self.shape_size[0],
                    self.entity.scale * self.shape_size[1]), (
                    other.entity.position[0], other.entity.position[1], other.entity.scale * other.shape_size[0],
                    other.entity.scale * other.shape_size[1])):
                self.on_collide(self.entity, other.entity)

    def draw(self, game):
        if self.texture is None:
            if self.shape == ShapeType.Circle_:
                game.draw_circle(self.entity.position[0], self.entity.position[1],
                                 self.entity.scale * self.shape_size[0],
                                 self.color)
            elif self.shape == ShapeType.Box_:
                game.draw_box(self.entity.position[0], self.entity.position[1], self.entity.scale * self.shape_size[0],
                              self.entity.scale * self.shape_size[1], self.color, True)
        else:
            game.draw_texture(self.entity.position[0], self.entity.position[1], self.texture, True)


class Controller(Component):
    def __init__(self, speed):
        super().__init__(ComponentType.Controller_)
        self.speed = speed

    def update(self, game):
        if game.is_key_down(pygame.K_w) or game.is_key_down(pygame.K_UP):
            self.entity.position[1] -= self.speed
        if game.is_key_down(pygame.K_s) or game.is_key_down(pygame.K_DOWN):
            self.entity.position[1] += self.speed
        if game.is_key_down(pygame.K_a) or game.is_key_down(pygame.K_LEFT):
            self.entity.position[0] -= self.speed
        if game.is_key_down(pygame.K_d) or game.is_key_down(pygame.K_RIGHT):
            self.entity.position[0] += self.speed


class Label(Component):
    def __init__(self, txt, offset, color, size: int = 20, center: bool = False):
        super().__init__(ComponentType.Label_)
        self.txt = txt
        self.color = color
        self.offset = offset
        self.center = center
        self.size = size

    def draw(self, game):
        game.draw_text(self.txt, self.entity.position[0] + self.offset[0], self.entity.position[1] + self.offset[1],
                       self.size,
                       self.color, self.center)


class Drift(Component):
    def __init__(self, direction, speed: int = 1):
        super().__init__(ComponentType.Drift_)
        self.direction = direction
        self.speed = speed

    def update(self, game):
        self.entity.position[0] += self.direction[0] * self.speed
        self.entity.position[1] += self.direction[1] * self.speed


def load_texture(path):
    full_path = os.path.dirname(os.path.abspath(__file__))
    return pygame.image.load(full_path + "/" + path)


def create_display(width, height, title="pygame-display"):
    pygame.display.init()
    display = pygame.display.set_mode((width, height), 0, 32)
    pygame.display.set_caption(title)
    return display, width, height


TO_REMOVE = []
ENTITIES = {}


def add_entity(entity):
    ENTITIES[entity.id] = entity


def remove_entity(entity):
    if entity.id in ENTITIES:
        TO_REMOVE.append(entity.id)


class Entity:
    _nextID = 0

    def __init__(self):
        self.position = [0, 0]
        self.scale = 1
        self.components = {}
        self.id = Entity._nextID
        Entity._nextID += 1

    def add_component(self, component):
        component.entity = self
        self.components[component.component_type] = component

    def update(self, game):
        for component in self.components.values():
            component.update(game)

    def draw(self, game):
        for component in self.components.values():
            component.draw(game)


# Part 3
# Custom components or entities here
#
# POLE_WIDTH = 64
# POLE_HEIGHT = 150
# SPAWN_OFFSET = 125
#
#
# class Pole(Entity):
#     def __init__(self, start_x, start_y):
#         super().__init__()
#         self.position = [start_x, start_y]
#         self.start_x = start_x
#         self.start_y = start_y
#         # Will make the pole slowly move to the left
#         self.add_component(Drift([-1, 0]))
#         self.add_component(Shape(ShapeType.Box_, [POLE_WIDTH, POLE_HEIGHT], pygame.Color(0x00ff00ff)))
#
#         def collide_callback(entity_a, entity_b):
#             remove_entity(entity_b)
#
#         self.components[ComponentType.Shape_].on_collide = collide_callback
#
#     def update(self, game):
#         super().update(game)
#         # If pole goes off left side of screen respawn to starting position
#         if self.position[0] <= -POLE_WIDTH:
#             self.position[0] = self.start_x
#
#     def draw(self, game):
#         super().draw(game)

# From Part 3
# Now to make a modified controller that just responds to the space bar
# class JumpController(Component):
#     def __init__(self, speed: int = 1, jump_speed: int = 2):
#         super().__init__(ComponentType.JumpController_)
#         self.speed = speed
#         self.jump_speed = jump_speed
#
#     def update(self, game):
#         if game.is_key_clicked(pygame.K_SPACE):
#             self.entity.position[1] -= self.jump_speed
#         if game.is_key_down(pygame.K_a) or game.is_key_down(pygame.K_LEFT):
#             self.entity.position[0] -= self.speed
#         if game.is_key_down(pygame.K_d) or game.is_key_down(pygame.K_RIGHT):
#             self.entity.position[0] += self.speed


# Part 4
WIDTH = 960
HEIGHT = 960
spark_tex = load_texture("charge.png")
fly_tex = load_texture("fly.png")
insulator_tex = load_texture("insulator.png")
minus_tex = load_texture("minus.png")
plus_tex = load_texture("plus.png")


class Fly(Entity):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.position = [x, y]
        shape = Shape(ShapeType.Circle_, [4], pygame.Color(0xffffffff))
        shape.texture = fly_tex
        self.add_component(shape)
        self.add_component(Controller(3))
        self.add_component(Drift([0, 1]))
        self.sparkCount = 0
        self.deathCount = 0
        self.start_position = [x, y]

    def draw(self, game):
        super().draw(game)
        game.draw_text("Sparks: " + str(self.sparkCount), self.position[0], self.position[1] - 16, 15,
                       pygame.Color(0xffffffff), True)


class Spark(Entity):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.position = [x, y]
        shape = Shape(ShapeType.Circle_, [8], pygame.Color(0xffffffff))

        def on_collide(entity_a, entity_b):
            remove_entity(entity_a)
            entity_b.sparkCount += 1

        shape.on_collide = on_collide
        shape.texture = spark_tex
        self.add_component(shape)


class Insulator(Entity):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.position = [x, y]
        shape = Shape(ShapeType.Box_, [16, 16], pygame.Color(0xffffffff))

        def on_collide(entity_a, entity_b):
            entity_b.position = entity_b.start_position.copy()
            entity_b.deathCount += 1

        shape.on_collide = on_collide
        shape.texture = insulator_tex
        self.add_component(shape)


class Minus(Entity):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.position = [x, y]
        shape = Shape(ShapeType.Circle_, [48], pygame.Color(0xffffffff))

        def on_collide(entity_a, entity_b):
            away = [entity_b.position[0] - entity_a.position[0], entity_b.position[1] - entity_a.position[1]]
            D = (away[0] ** 2 + away[1] ** 2) ** .5
            n_x = away[0] / D
            n_y = away[1] / D
            entity_b.position[0] += 0.1 * n_x * n_x
            entity_b.position[1] += 0.1 * n_y * n_y

        shape.on_collide = on_collide
        shape.texture = minus_tex
        self.add_component(shape)


class Plus(Entity):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.position = [x, y]
        shape = Shape(ShapeType.Circle_, [48], pygame.Color(0xffffffff))

        def on_collide(entity_a, entity_b):
            away = [entity_b.position[0] - entity_a.position[0], entity_b.position[1] - entity_a.position[1]]
            D = (away[0] ** 2 + away[1] ** 2) ** .5
            entity_b.position[0] -= 0.5 * away[0] / D
            entity_b.position[1] -= 0.5 * away[1] / D

        shape.on_collide = on_collide
        shape.texture = plus_tex
        self.add_component(shape)


TILE_SIZE = 16


def gen_map(width, height):
    map = [0 for i in range(width * height)]
    player_x, player_y = random.randint(1, width - 2), random.randint(1, height - 2)
    for i in range(0, height):
        for j in range(0, width):
            if i == 0 or j == 0 or i == height - 1 or j == width - 1:
                map[j + i * width] = "I"
            elif random.random() < 0.05:
                x_width = random.randint(1, 7)
                y_height = 1 if x_width != 1 else random.randint(2, 7)
                for u in range(i, min(i + y_height, height)):
                    for v in range(j, min(j + x_width, width)):
                        map[v + u * width] = "I"
            elif random.random() < 0.025:
                map[j + i * width] = "S"
            elif random.random() < 0.05:
                if random.random() < 0.5:
                    map[j + i * width] = "M"
                else:
                    map[j + i * width] = "P"
            else:
                map[j + i * width] = "B"
    map[player_x + player_y * width] = "F"
    return map


HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = WIDTH // 2
MAP_WIDTH = HALF_WIDTH // TILE_SIZE
MAP_HEIGHT = HALF_HEIGHT // TILE_SIZE


class SparkCounter:
    count = 0


class LevelCounter:
    count = 0


fly = Fly(0, 0)


def create_world():
    MAP = gen_map(MAP_WIDTH, MAP_HEIGHT)
    fly_pos = [0, 0]
    SparkCounter.count = 0
    for j in range(0, MAP_HEIGHT):
        for i in range(0, MAP_WIDTH):
            tile = MAP[i + j * MAP_WIDTH]
            if tile == 'S':
                add_entity(
                    Spark(i * TILE_SIZE + TILE_SIZE // 2, j * TILE_SIZE + TILE_SIZE // 2))
                SparkCounter.count += 1
            elif tile == 'F':
                fly_pos = [i * TILE_SIZE + TILE_SIZE // 2, j * TILE_SIZE + TILE_SIZE // 2]
            elif tile == 'I':
                add_entity(Insulator(i * TILE_SIZE + TILE_SIZE // 2, j * TILE_SIZE + TILE_SIZE // 2))
            elif tile == 'M':
                add_entity(
                    Minus(i * TILE_SIZE + TILE_SIZE // 2, j * TILE_SIZE + TILE_SIZE // 2))
            elif tile == 'P':
                add_entity(
                    Plus(i * TILE_SIZE + TILE_SIZE // 2, j * TILE_SIZE + TILE_SIZE // 2))
    for e_a in ENTITIES.values():
        for e_b in ENTITIES.values():
            if e_a.id != e_b.id:
                e_a.components[ComponentType.Shape_].ignore(e_b)
    fly.position = fly_pos.copy()
    fly.start_position = fly_pos.copy()
    fly.sparkCount = 0
    add_entity(fly)


class Game:
    def __init__(self):
        self.running = True
        self.user_exit = False
        self.keys_clicked = {}
        self.buttons_clicked = {}
        self.keys_down = []
        self.buttons_down = []
        self.key_mods = 0
        self.mouse_position = [0, 0]
        self.previous_mouse_position = [0, 0]
        self.mouse_velocity = [0, 0]
        self.display = None
        self.current_frame = None
        self.width = 0
        self.height = 0

    def init(self, width=WIDTH, height=HEIGHT, pixel_scale=2):
        self.current_frame = pygame.Surface((width / pixel_scale, height / pixel_scale))
        self.display, self.width, self.height = create_display(width, height, "SparkFly")
        pygame.font.init()
        # From Part 3
        # Map and entity initialization
        # adds 20 poles to the bottom and top of a 1600x900 window but off to the right of the screen
        # for i in range(0, 10):
        #     add_entity(Pole(1600 + i * (POLE_WIDTH + SPAWN_OFFSET), POLE_HEIGHT // 2))
        #     add_entity(Pole(1600 + i * (POLE_WIDTH + SPAWN_OFFSET), 900 - POLE_HEIGHT // 2))

        # None of the entities in the map will collide with each other
        # IMPORTANT: do this before adding your player
        # for pole_a in ENTITIES.values():
        #     for pole_b in ENTITIES.values():
        #         if pole_a.id != pole_b.id:
        #             pole_a.components[ComponentType.Shape_].ignore(pole_b)

        # player = Entity()
        # Gravity
        # player.add_component(Drift([0, 1]))
        # User controls
        # player.add_component(JumpController(1, 75))
        # player.add_component(Shape(ShapeType.Circle_, [32], pygame.Color(0xff0000ff)))
        # add_entity(player)
        create_world()

    def poll_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_clicked[event.key] = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.buttons_clicked[event.button] = True
        self.keys_down = pygame.key.get_pressed()
        self.buttons_down = pygame.mouse.get_pressed()
        self.key_mods = pygame.key.get_mods()
        tuple_mouse_pos = pygame.mouse.get_pos()
        self.mouse_position[0] = tuple_mouse_pos[0]
        self.mouse_position[1] = tuple_mouse_pos[1]
        if self.previous_mouse_position[0] != self.mouse_position[0] and self.previous_mouse_position[1] != \
                self.mouse_position[1]:
            self.mouse_velocity[0] = self.mouse_position[0] - self.previous_mouse_position[0]
            self.mouse_velocity[1] = self.mouse_position[1] - self.previous_mouse_position[1]
            self.previous_mouse_position = self.mouse_position.copy()

    def is_key_down(self, key):
        return self.keys_down[key]

    def is_key_clicked(self, key):
        return key in self.keys_clicked and self.keys_clicked[key]

    def is_button_down(self, button):
        return self.buttons_down[button]

    def is_button_clicked(self, button):
        return button in self.buttons_clicked and self.buttons_clicked[button]

    def is_key_mod(self, key_mod):
        return self.key_mods & key_mod

    def get_scroll(self):
        if self.is_button_clicked(3):
            return -1
        if self.is_button_clicked(4):
            return 1
        return 0

    def update(self):
        for entity in ENTITIES.values():
            entity.update(self)
        for e_a in ENTITIES.values():
            for e_b in ENTITIES.values():
                if e_a.id != e_b.id:
                    try:
                        e_a.components[ComponentType.Shape_].colliding_with(e_b.components[ComponentType.Shape_])
                    except KeyError:
                        pass
        for eid in TO_REMOVE:
            ENTITIES.pop(eid)
        TO_REMOVE.clear()
        # Part 4
        pygame.display.set_caption("SparkyFly | Deaths "+str(fly.deathCount))
        if fly.sparkCount >= SparkCounter.count:
            LevelCounter.count += 1
            ENTITIES.clear()
            if LevelCounter.count < 10:
                create_world()
            else:
                exit()

    def clear_input(self):
        self.keys_clicked.clear()
        self.buttons_clicked.clear()

    def clear(self):
        # clears to black
        self.current_frame.fill(pygame.Color(0x000000ff))

    def draw_circle(self, x: int, y: int, radius: int, color: pygame.Color):
        pygame.draw.circle(self.current_frame, color, (x, y), radius)

    def draw_box(self, x: int, y: int, width: int, height: int, color: pygame.Color, center: bool = False):
        pos = (x, y) if not center else (x - width // 2, y - height // 2)
        pygame.draw.rect(self.current_frame, color, (pos[0], pos[1], width, height))

    def draw_line(self, sx: int, sy: int, ex: int, ey: int, color: pygame.Color, thickness: int = 1):
        pygame.draw.line(self.current_frame, color, (sx, sy), (ex, ey), thickness)

    def draw_text(self, txt: str, x: int, y: int, size: int, color: pygame.Color, center: bool = False):
        f = pygame.font.Font(None, size)
        font_screen = f.render(txt, True, color)
        pos = (x, y) if not center else (x - font_screen.get_width() // 2, y - font_screen.get_height() // 2)
        self.current_frame.blit(font_screen, pos)

    def draw_texture(self, x: int, y: int, texture_frame, center: bool = False):
        pos = (x, y) if not center else (x - texture_frame.get_width() // 2, y - texture_frame.get_height() // 2)
        self.current_frame.blit(texture_frame, pos)

    def render(self):
        for entity in ENTITIES.values():
            entity.draw(self)

    def swap_frame(self):
        self.display.blit(pygame.transform.scale(self.current_frame, self.display.get_rect().size), (0, 0))
        pygame.display.update()
        pygame.display.flip()

    def run(self):
        self.init()
        while self.running:
            self.poll_input()
            self.update()
            self.clear_input()
            self.clear()
            self.render()
            self.swap_frame()


Game().run()
