from kivy.app import App
import math
import random
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.metrics import Metrics
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.config import Config
from kivy.animation import Animation
from kivy.core.image import Image
import vertex.numbers

WINDOW_HEIGHT = Window.height
WINDOW_WIDTH = Window.width


def euclidean_distance(pos1=(0, 0), pos2=(0, 0)):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


# klasa przedstawiająca koło
class Circle(Ellipse):
    def __init__(self, pos=(0, 0), radius: float = 0):
        return_pos = (pos[0] - radius, pos[1] - radius)
        return_size = (2 * radius, 2 * radius)
        super().__init__(pos=return_pos, size=return_size)


# kółko pojawiające się przy dotknięciu ekranu
class TouchIndicator(Widget):
    def __init__(self, touch_id, color):
        super().__init__()
        self.touch_id = touch_id
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        self.is_color_recyclable = color[3]
        self.start_angle = random.random() * 360
        self.arch_angle = 20
        self.drain_angle_start = 0
        self.size = (0.8 * Metrics.cm, 0.8 * Metrics.cm)
        self.fill_done = False
        self.number = False
        self.is_drain_running = False
        self.encircle = []
        self.draining_angle = 0
        self.drained_angle = 0
        self.drain_move_seconds = 0

    def choice_display(self, place, out_of):
        self.number = place + 1  # zaczyna się od 0
        self.is_drain_running = True  # todo drain animation?
        if self.is_connected_to_order_tracker():
            input_handler.order_trackers.get(self.number).set_color(self.red, self.green, self.blue)
            input_handler.order_trackers.get(self.number).draw()
        input_handler.animation.stop(self)
        input_handler.animation_shrink.start(self)

    def is_connected_to_order_tracker(self):
        if self.number > input_handler.max_trackers:
            return False
        return True

    @staticmethod
    def end_angle(angle_start, arch_angle):
        end_angle = angle_start + arch_angle
        if end_angle >= 360:
            end_angle -= 360
        return end_angle

    def outline_instructions(self):
        if self.arch_angle == 0:
            return
        if self.arch_angle == 360:
            Line(width=0.04 * Metrics.cm, cap='round', circle=(self.pos[0], self.pos[1], self.size[0]))
        elif self.end_angle(self.start_angle, self.arch_angle) > self.start_angle:
            Line(width=0.04 * Metrics.cm, cap='round',
                 circle=(self.pos[0], self.pos[1], self.size[0], self.start_angle,
                         self.end_angle(self.start_angle, self.arch_angle)))
        else:
            Line(width=0.04 * Metrics.cm, cap='round',
                 circle=(self.pos[0], self.pos[1], self.size[0], self.start_angle, 360))
            Line(width=0.04 * Metrics.cm, cap='round',
                 circle=(self.pos[0], self.pos[1], self.size[0], 0, self.end_angle(self.start_angle, self.arch_angle)))

    def set_start_angle(self, angle):
        if angle >= 360:
            self.start_angle = angle - 360
        else:
            self.start_angle = angle

    def set_arch_angle(self, angle):
        if angle >= 360:
            self.arch_angle = 360
        else:
            self.arch_angle = angle

    @staticmethod
    def set_general_angle_restricted(angle):
        if angle >= 360:
            angle = 360
        elif angle < 0:
            angle = 0
        return angle

    @staticmethod
    def set_general_angle_cycling(angle):
        if angle > 360:
            angle -= angle % 360
        elif angle < 0:
            angle += abs(angle) % 360
        return angle

    def set_specialcase_angle_restricted(self, angle, restriction_angle, restricted_area_start, restricted_area_end):
        if angle > 360:
            angle -= 360
        elif angle < 0:
            angle += 360
        if angle > restricted_area_start and angle < restricted_area_end:
            angle = restriction_angle
        return angle

    def cycle_outline(self, delta_time, frequency):
        self.set_start_angle(self.start_angle + (delta_time / frequency) * 360)

    def outline_animation_fill(self, delta_time, fill_rate, start_angle_move):
        if not self.fill_done:
            if self.arch_angle == 360:
                self.fill_done = True
                return True
            self.set_start_angle(self.start_angle + start_angle_move * delta_time)
            self.set_arch_angle(self.arch_angle + fill_rate * delta_time)

    def outline_animation_drain(self, dt, drain_rate):
        if not self.is_drain_running:
            return False
        if self.arch_angle == 0 and not self.is_connected_to_order_tracker():
            self.is_drain_running = False
            return True
        if self.is_connected_to_order_tracker():
            order_tracker = input_handler.order_trackers.get(self.number)
            encircle_info = order_tracker.calculate_circle_from_touch_indicator(self)
            self.draining_angle = encircle_info[1]

        self.drained_angle = self.set_general_angle_restricted(dt * drain_rate + self.drained_angle)
        self.set_start_angle(self.draining_angle + self.drained_angle)
        self.set_arch_angle(360 - self.drained_angle)
        if not self.is_connected_to_order_tracker():
            return

        if self.arch_angle == 0:
            self.drain_move_seconds += dt
        circum_rate = encircle_info[2]
        move_rate_encircle = drain_rate * circum_rate
        arch_angle_encircle = self.set_general_angle_restricted(self.drained_angle * circum_rate)

        if self.pos[1] - self.size[0] < order_tracker.pos[1]:
            start_angle_encircle = self.set_general_angle_restricted(
                encircle_info[1] + move_rate_encircle * self.drain_move_seconds)
            end_angle_encircle = self.set_general_angle_restricted(start_angle_encircle + arch_angle_encircle)
        elif self.pos[0] > order_tracker.pos[0]:
            start_angle_encircle = self.set_general_angle_restricted(
                encircle_info[1] + move_rate_encircle * self.drain_move_seconds + 180) - 180
            end_angle_encircle = self.set_general_angle_restricted(
                start_angle_encircle + arch_angle_encircle + 180) - 180
        else:
            end_angle_encircle = self.set_general_angle_restricted(
                encircle_info[1] - move_rate_encircle * self.drain_move_seconds - 180) + 180  # idzie w drugą stronę
            start_angle_encircle = self.set_general_angle_restricted(
                end_angle_encircle - arch_angle_encircle - 180) + 180

        encircle = encircle_info[0]
        encircle.append(start_angle_encircle)
        encircle.append(end_angle_encircle)
        self.encircle = encircle

        if self.pos[1] - self.size[0] < order_tracker.pos[1]:
            if end_angle_encircle == 360:
                input_handler.order_trackers.get(self.number).fill(drain_rate)
            if start_angle_encircle == 360:
                self.is_drain_running = False
                return True
        else:
            if start_angle_encircle == 180:
                input_handler.order_trackers.get(self.number).fill(drain_rate)
            if end_angle_encircle == 180:
                self.is_drain_running = False
                return True

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(self.red, self.green, self.blue)
            Circle(self.pos, 0.75 * self.size[0])
            self.outline_instructions()
            if self.is_drain_running and self.is_connected_to_order_tracker():
                Line(width=0.04 * Metrics.cm, circle=self.encircle)
            if self.number:
                Color(0, 0, 0)
                Numbers.method(self.number)(0.6 * self.size[0], self.pos, self.number)

    def self_destruct(self):
        pass  # todo deletion from memory

    def delete(self):
        self.canvas.clear()
        if self.is_color_recyclable:
            input_handler.color_palette.recycle_color([self.red, self.green, self.blue, self.is_color_recyclable])


class OrderTracker(Widget):
    def __init__(self, number):
        x = WINDOW_WIDTH - 1 * Metrics.cm
        y = WINDOW_HEIGHT - 2 * Metrics.mm - 5 * Metrics.mm * (number - 1)
        super().__init__(pos=(x, y))
        self.red = 0
        self.green = 0
        self.blue = 0
        self.end_point = [self.pos[0], self.pos[1]]
        self.is_imploding = False
        self.fill_rate = 0

    FILL_RATE_CONVERSION = Metrics.mm / 5000
    IMPLODE_RATE = Metrics.cm

    def calculate_circle_from_touch_indicator(self, touch_indicator):
        x1 = self.pos[0]  # ==x2
        y2 = self.pos[1]
        x3 = touch_indicator.pos[0]
        y3 = touch_indicator.pos[1]
        r = touch_indicator.size[0]
        a = 4 * ((y2 ** 2) - 2 * y2 * y3 + (y3 ** 2) - (r ** 2))
        b = 4 * (-(y2 ** 3) + y2 * (r ** 2) + y2 * (y3 ** 2) + (x3 ** 2) * y2 + y2 * (
                x1 ** 2) - 2 * y2 * x1 * x3 - y3 * (r ** 2) - (y3 ** 3) - (x3 ** 2) * y3 - y3 * (x1 ** 2) + (
                         y2 ** 2) * y3 + 2 * x1 * x3 * y3 + 2 * (r ** 2) * y3)
        c = (y2 ** 4) - 2 * (y2 ** 2) * (r ** 2) - 2 * (y2 ** 2) * (y3 ** 2) - 2 * (y2 ** 2) * (x3 ** 2) - 2 * (
                y2 ** 2) * (x1 ** 2) + 4 * (y2 ** 2) * x1 * x3 + (r ** 4) + 2 * (r ** 2) * (y3 ** 2) + 2 * (
                    r ** 2) * (x3 ** 2) + 2 * (r ** 2) * (x1 ** 2) - 4 * (r ** 2) * x1 * x3 + (y3 ** 4) + 2 * (
                    x3 ** 2) * (y3 ** 2) + 2 * (y3 ** 2) * (x1 ** 2) - 4 * x1 * x3 * (y3 ** 2) + (x3 ** 4) + 2 * (
                    x1 ** 2) * (x3 ** 2) - 4 * x1 * (x3 ** 3) + (x1 ** 4) - 4 * (x1 ** 3) * x3 + 4 * (x1 ** 2) * (
                    x3 ** 2) - 4 * (r ** 2) * (y3 ** 2) - 4 * (r ** 2) * (x3 ** 2) + 8 * x3 * x1 * (r ** 2) - 4 * (
                    x1 ** 2) * (r ** 2)
        delta = (b ** 2) - 4 * a * c
        if delta < 0:
            # print("bad delta tho")
            return False
        y1_1 = (-b - math.sqrt(delta)) / (2 * a)
        y1_2 = (-b + math.sqrt(delta)) / (2 * a)
        y1 = min(y1_1, y1_2)
        R = abs(y2 - y1)
        alfa = math.degrees(math.atan2(x3 - x1, y3 - y1))
        if alfa < 0:
            alfa += 360
        circumference_rate = r / R
        return [[x1, y1, R], alfa, circumference_rate]

    def calculate_line_from_touch_indicator(self, touch_indicator):  # unused
        y = self.pos[1]
        x = self.pos[0]
        x1 = touch_indicator.pos[0]
        y1 = touch_indicator.pos[1]
        r = touch_indicator.size[0]
        a = (y1 - y) / (x1 - x)
        xr = math.sqrt((r ** 2) / (a ** 2 + 1)) + x1
        yr = math.sqrt((r ** 2) / ((1 / a) ** 2 + 1)) + y1
        points = [(x, y), (xr, yr)]
        Line(width=0.04 * Metrics.cm, points=points)
        return math.atan(a)

    def draw(self):
        self.canvas.clear()
        if self.fill_rate > 0:
            self.end_point[0] += self.fill_rate * OrderTracker.FILL_RATE_CONVERSION
        if self.end_point[0] >= WINDOW_WIDTH:
            self.fill_rate = 0
        if self.pos == self.end_point:
            return
        with self.canvas:
            Color(self.red, self.green, self.blue)
            points = [self.pos, self.end_point]
            Line(width=0.1 * Metrics.cm, points=points)

    def fill(self, fill_rate):
        self.fill_rate = fill_rate

    def set_color(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

    def implode(self):
        self.is_imploding = True

    def implode_process(self, dt):
        self.pos[0] += OrderTracker.IMPLODE_RATE * dt
        if self.pos[0] >= WINDOW_WIDTH:
            self.set_color(0, 0, 0)
            self.pos[0] = WINDOW_WIDTH - 1 * Metrics.cm
            self.end_point[0] = self.pos[0]
            self.is_imploding = False


class ColorPalette():
    def __init__(self):
        self.colors = []
        are_colors_recyclable = True
        color_codes = ["F1232F", "FA8126", "FFE65A", "9FE302", "2461AF", "8B4256", "6F1918", "A14224", "BA9A37",
                       "5B5823", "2F4B73", "532D52", "FFFFFF", "888888"]
        for code in color_codes:
            color = ColorPalette.convert_from_hex_colors(code)
            color.append(are_colors_recyclable)
            self.colors.append(color)

    @staticmethod
    def convert_from_hex_colors(hex_color):
        if len(hex_color) != 6:
            return

        def to_numbers(character):
            if character == 'F':
                return 15
            elif character == 'E':
                return 14
            elif character == 'D':
                return 13
            elif character == 'C':
                return 12
            elif character == 'B':
                return 11
            elif character == 'A':
                return 10
            else:
                return int(character)

        red = (16 * to_numbers(hex_color[0]) + to_numbers(hex_color[1])) / 255
        green = (16 * to_numbers(hex_color[2]) + to_numbers(hex_color[3])) / 255
        blue = (16 * to_numbers(hex_color[4]) + to_numbers(hex_color[5])) / 255
        return [red, green, blue]

    def take_color(self):
        if len(self.colors) > 0:
            rand = math.floor(random.random() * len(self.colors))
            color = self.colors.pop(rand)
            return color
        else:
            return ColorPalette.generate_color()

    @staticmethod
    def generate_color():
        red = random.random()
        green = random.random()
        blue = random.random()
        is_recyclable = False
        if red > blue and red > green:
            ratio = .99 / red
        elif blue > green:
            ratio = .99 / blue
        else:
            ratio = .99 / green
        red *= ratio
        green *= ratio
        blue *= ratio
        return [red, green, blue, is_recyclable]

    def recycle_color(self, color):
        self.colors.append(color)


# dystrybutor eventów
class InputHandler():
    def __init__(self):
        # print("ih init")
        self.color_palette = ColorPalette()
        self.touch_indicators = {}
        self.blacklist_touches = []
        self.ti_to_remove = []
        self.order_trackers = {}
        self.chosen_indicators = []
        self.root_widget = None
        self.animation = Animation(size=(1 * Metrics.cm, 1 * Metrics.cm), duration=.7) + Animation(
            size=(0.8 * Metrics.cm, 0.8 * Metrics.cm), duration=.7)
        self.animation.repeat = True
        self.animation_shrink = Animation(size=(0.8 * Metrics.cm, 0.8 * Metrics.cm), duration=.4)
        self.tick_event = None
        self.is_choice_running = False
        self.is_choice_done = False
        self.choice_timer = 0
        self.max_trackers = (WINDOW_HEIGHT - 2 * Metrics.mm) / (5 * Metrics.mm)
        self.DEL_TIME_MAX = 1
        self.chosen_deletion_timer = self.DEL_TIME_MAX
        self.is_chosen_deletion_running = False
        self.animation_implode = Animation(size=(1, 1), duration=self.DEL_TIME_MAX)

    def choice_process(self):
        if self.choice_timer < 120:
            self.choice_timer += 1
        else:
            places = []
            for u in self.touch_indicators:
                places.append(len(places))
            number_places = len(places)
            for ti in self.touch_indicators.values():
                self.chosen_indicators.append(ti)
                place = math.floor(random.random() * len(places))
                ti.choice_display(places.pop(place), number_places)
            self.is_choice_running = False
            self.is_choice_done = True

    def on_move(self, event, etype, me):
        if not me.is_touch:
            return
        if me.uid in self.blacklist_touches:
            return
        pos = me.to_absolute_pos(me.sx, me.sy, WINDOW_WIDTH, WINDOW_HEIGHT, 0)
        if me.uid not in self.touch_indicators:
            ti = TouchIndicator(me.uid, self.color_palette.take_color())
            self.touch_indicators[me.uid] = ti
            self.root_widget.add_widget(ti)
            self.animation.start(ti)
            self.update_choice_countdown_state()
        if len(self.touch_indicators) > len(self.order_trackers):
            number = len(self.order_trackers) + 1
            if not number > self.max_trackers:
                ot = OrderTracker(number)
                self.order_trackers[number] = ot
                self.root_widget.add_widget(ot)
        self.touch_indicators[me.uid].pos = pos

    def on_release(self, event, touch):
        if touch.uid in self.blacklist_touches:
            self.blacklist_touches.remove(touch.uid)
            return
        if touch.uid not in self.touch_indicators.keys():
            ti = self.touch_indicators.pop(touch.uid)
            self.ti_to_remove.append(ti)
            return
        if self.chosen_indicators.count(self.touch_indicators.get(touch.uid)) == 0:
            ti = self.touch_indicators.pop(touch.uid)
            ti.delete()
            input_handler.animation.cancel(ti)
            input_handler.root_widget.remove_widget(ti)
            # if self.chosen_indicators.count(ti) > 0: ### todo zrobić usuwanie ti już użytych do losowania
            #    self.chosen_indicators.remove(ti)

    def check_if_any_chosen(self):
        if len(self.chosen_indicators) > 0:
            return True
        return False

    def chosen_deletion_countdown_start(self):
        self.is_chosen_deletion_running = True
        for ti in self.chosen_indicators:
            # print("buujaa")
            Animation.cancel_all(ti)
            self.animation_implode.start(ti)

    def chosen_deletion_countdown(self, dt):
        self.chosen_deletion_timer -= dt
        if self.chosen_deletion_timer > 0:
            return
        # print(self.chosen_deletion_timer)
        for ti in self.chosen_indicators:
            ti.delete()
            self.animation.cancel(ti)
            self.root_widget.remove_widget(ti)
            if is_in_iterable(self.touch_indicators.keys(), ti.touch_id):
                self.touch_indicators.pop(ti.touch_id)
                self.blacklist_touches.append(ti.touch_id)
            if self.ti_to_remove.count(ti) > 0:
                self.ti_to_remove.remove(ti)
            self.chosen_indicators.remove(ti)
        for ot in self.order_trackers.values():
            ot.implode()
        if len(self.chosen_indicators) == 0:
            self.chosen_deletion_countdown_reset()
            self.update_choice_countdown_state()

    def chosen_deletion_countdown_reset(self):
        self.chosen_deletion_timer = self.DEL_TIME_MAX
        self.is_chosen_deletion_running = False
        for ti in self.chosen_indicators:
            Animation.cancel_all(ti)
            self.animation_shrink.start(ti)

    def update_choice_countdown_state(self):
        if len(self.touch_indicators) >= 2 and not len(self.chosen_indicators) > 0:
            self.is_choice_running = True
            self.choice_timer = 0
        else:
            self.is_choice_running = False


def is_in_iterable(iterable, thing):
    for i in iterable:
        if i == thing:
            return True
    return False


# main
class MyApp(App):
    def build(self):
        Window.bind(on_motion=input_handler.on_move)
        Window.bind(on_touch_up=input_handler.on_release)
        widget = Widget(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        input_handler.root_widget = widget
        input_handler.tick_event = Clock.schedule_interval(self.frametick, 1 / Config.getint('graphics', 'maxfps'))
        return widget

    def frametick(self, dt):
        # print(len(input_handler.chosen_indicators))
        # print(len(input_handler.touch_indicators))
        # print(len(input_handler.ti_to_remove))
        # print()
        # print(Clock.get_fps())
        self.update_chosen_deletion()
        if input_handler.is_chosen_deletion_running:
            input_handler.chosen_deletion_countdown(dt)
        for ti in input_handler.touch_indicators.values():
            ti.outline_animation_fill(dt, 360, 200)
            ti.outline_animation_drain(dt, 720)
            ti.draw()
        for ti in input_handler.ti_to_remove:
            ti.outline_animation_fill(dt, 360, 200)
            ti.outline_animation_drain(dt, 720)
            ti.draw()
            if not ti.is_drain_running:
                pass
        for ot in input_handler.order_trackers.values():
            ot.draw()
            if ot.is_imploding:
                ot.implode_process(dt)
        if input_handler.is_choice_running:
            input_handler.choice_process()

    @staticmethod
    def update_chosen_deletion():
        if not input_handler.check_if_any_chosen():
            return
        if input_handler.is_chosen_deletion_running:
            should_be_reset = True
            for ti in input_handler.touch_indicators.values():
                if ti not in input_handler.chosen_indicators:
                    should_be_reset = False
                    break
            if should_be_reset:
                input_handler.chosen_deletion_countdown_reset()
        else:
            for ti in input_handler.touch_indicators.values():
                if ti not in input_handler.chosen_indicators:
                    input_handler.chosen_deletion_countdown_start()
                    break


Numbers = vertex.numbers.Numbers()
input_handler = InputHandler()
MyApp().run()
# TODO: animacje obwódki idące w dół jak muszą
# usuwanie z pamięci obiektów jak zakończą swoje animacje
