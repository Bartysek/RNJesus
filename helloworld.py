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

WINDOW_HEIGHT=Window.height
WINDOW_WIDTH=Window.width

def euclidean_distance(pos1=(0,0),pos2=(0,0)):
    return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

#klasa przedstawiająca koło
class Circle(Ellipse):
    def __init__(self,pos=(0,0),radius=0):
        return_pos=(pos[0]-radius,pos[1]-radius)
        return_size=(2*radius,2*radius)
        return super().__init__(pos=return_pos,size=return_size)

#kółko pojawiające się przy dotknięciu ekranu
class TouchIndicator(Widget):
    def __init__(self,touch_id):
        super().__init__()
        self.touch_id=touch_id
        self.start_angle=random.random()*360
        self.arch_angle=20
        self.drain_angle_start=0
        self.size=(0.8*Metrics.cm,0.8*Metrics.cm)
        self.fill_done=False
        self.segments = [[random.random()*360,60]]
        self.red=random.random()
        self.green=random.random()
        self.blue=random.random()
        self.number=False
        self.is_drain_running=False
        self.encircle=[]
        self.draining_angle=0
        self.drained_angle=0
        self.drain_move_seconds=0

    def choice_display(self,place,out_of):
        self.number=place+1 #zaczyna się od 0
        self.is_drain_running=True #todo drain animation
        if self.number <= input_handler.max_trackers:
            input_handler.order_trackers.get(self.number).set_color(self.red,self.green,self.blue)
            input_handler.order_trackers.get(self.number).draw()
        input_handler.animation.stop(self)
        input_handler.animation_shrink.start(self)
        
    def is_connected_to_order_tracker(self):
        if self.number > input_handler.max_trackers:
            return False
        return True
    
    def choice_segments(self,place,out_of): #archiwalne
        self.segments.clear()       
        arch_angle=min((360/out_of)*8/10,360/out_of-9)
        centering_angle=((360/out_of)-arch_angle)/2
        for i in range(place+1):
            self.segments.append([0,0])
            self.segments[i][0]=i*(360/out_of)+centering_angle
            self.segments[i][1]=arch_angle
        
    def end_angle(self, angle_start, arch_angle):
        end_angle=angle_start+arch_angle
        if end_angle>=360:
            end_angle-=360
        return end_angle

    def outline_segment(self,angle_start,arch_angle):
        if arch_angle==0:
            return
        if arch_angle==360:
            Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0]))
        elif self.end_angle(angle_start,arch_angle)>angle_start:
            Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0],angle_start,self.end_angle(angle_start,arch_angle)))
        else:
            Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0],angle_start,360))           
            Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0],0,self.end_angle(angle_start,arch_angle)))
   
    def outline_instructions(self):
        for segment in self.segments:
                self.outline_segment(segment[0],segment[1])          

    def set_start_angle(self,angle):
        if angle>=360:
            self.segments[0][0]=angle-360
        else:
            self.segments[0][0]=angle

    def set_arch_angle(self,angle):
        if angle>=360:
            self.segments[0][1]=360
        else:
            self.segments[0][1]=angle

    def set_general_angle_restricted(self,angle):
        ret=angle
        if angle>=360:
            ret=360
        elif angle<0:
            ret=0
        return ret
            
    def cycle_outline(self,dt,frequency):
        self.set_start_angle(self.segments[0][0]+(dt/frequency)*360)

    def outline_animation_fill(self,dt,fill_rate,start_angle_move):
        if not self.fill_done:
            if self.segments[0][1]==360:
                self.fill_done = True
                return True
            self.set_start_angle(self.segments[0][0]+start_angle_move*dt)
            self.set_arch_angle(self.segments[0][1]+fill_rate*dt)

    def outline_animation_drain(self,dt,drain_rate):
        if not self.is_drain_running:
            return False
        if self.segments[0][1]==0 and self.number > input_handler.max_trackers:
            self.is_drain_running = False
            return True
        if self.number <= input_handler.max_trackers:
            order_tracker=input_handler.order_trackers.get(self.number)
            encircle_info=order_tracker.calculate_circle_from_touch_indicator(self)
            self.draining_angle=encircle_info[1]
        self.drained_angle=self.set_general_angle_restricted(dt*drain_rate+self.drained_angle)
        self.set_start_angle(self.draining_angle+self.drained_angle)
        self.set_arch_angle(360-self.drained_angle)
        if self.number <= input_handler.max_trackers:
            if self.pos[1]-self.size[0] < order_tracker.pos[1]:
                if self.segments[0][1]==0:
                    self.drain_move_seconds+=dt
                circum_rate=encircle_info[2]
                move_rate_encircle=drain_rate*circum_rate
                arch_angle_encircle=self.set_general_angle_restricted(self.drained_angle*circum_rate)
                start_angle_encircle=self.set_general_angle_restricted(encircle_info[1]+move_rate_encircle*self.drain_move_seconds)
                end_angle_encircle=self.set_general_angle_restricted(start_angle_encircle+arch_angle_encircle)
                #print(start_angle_encircle)
                #print(end_angle_encircle)
                #print()
                encircle = encircle_info[0]
                encircle.append(start_angle_encircle)
                encircle.append(end_angle_encircle)
                self.encircle=encircle
                if end_angle_encircle==360:
                    input_handler.order_trackers.get(self.number).fill(drain_rate)
                if start_angle_encircle==360:
                    self.is_drain_running = False
                    return True
            else:
                if self.segments[0][1]==0:
                    self.drain_move_seconds+=dt
                circum_rate=encircle_info[2]
                move_rate_encircle=drain_rate*circum_rate
                arch_angle_encircle=self.set_general_angle_restricted(self.drained_angle*circum_rate)
                end_angle_encircle=self.set_general_angle_restricted(encircle_info[1]-move_rate_encircle*self.drain_move_seconds-180)+180 #idzie w drugą stronę
                start_angle_encircle=self.set_general_angle_restricted(end_angle_encircle-arch_angle_encircle-180)+180
                print(start_angle_encircle)
                print(end_angle_encircle)
                print()
                encircle = encircle_info[0]
                encircle.append(start_angle_encircle)
                encircle.append(end_angle_encircle)
                self.encircle=encircle
                if start_angle_encircle==180:
                    input_handler.order_trackers.get(self.number).fill(drain_rate)
                if end_angle_encircle==180:
                    self.is_drain_running = False
                    return True
            
    def circle(self):
        self.canvas.clear()
        with self.canvas:
            Color(self.red,self.green,self.blue)
            Circle(self.pos,0.75*self.size[0])
            self.outline_instructions()
            if self.is_drain_running and self.is_connected_to_order_tracker():
                Line(width=0.04*Metrics.cm,circle=self.encircle)
            if self.number:
                Color(0,0,0)
                Numbers.method(self.number)(0.6*self.size[0],self.pos,self.number)

    def self_destruct(self):
        pass
        
    def delete(self):
        self.canvas.clear()

class OrderTracker(Widget):
    def __init__(self, number):
        x=WINDOW_WIDTH-1*Metrics.cm
        y=WINDOW_HEIGHT-2*Metrics.mm-5*Metrics.mm*(number-1)
        super().__init__(pos=(x,y))
        self.red=0
        self.green=0
        self.blue=0
        self.end_point=[self.pos[0],self.pos[1]]
        self.is_imploding=False
        self.fill_rate=0

    FILL_RATE_CONVERSION=Metrics.mm/5000
    IMPLODE_RATE=Metrics.cm
    
    def calculate_circle_from_touch_indicator(self, touch_indicator):
        x1=self.pos[0] #==x2
        y2=self.pos[1]
        x3=touch_indicator.pos[0]
        y3=touch_indicator.pos[1]
        r=touch_indicator.size[0]
        a=4*((y2**2)-2*y2*y3+(y3**2)-(r**2))
        b=4*(-(y2**3)+y2*(r**2)+y2*(y3**2)+(x3**2)*y2+y2*(x1**2)-2*y2*x1*x3-y3*(r**2)-(y3**3)-(x3**2)*y3-y3*(x1**2)+(y2**2)*y3+2*x1*x3*y3+2*(r**2)*y3)
        c=(y2**4)-2*(y2**2)*(r**2)-2*(y2**2)*(y3**2)-2*(y2**2)*(x3**2)-2*(y2**2)*(x1**2)+4*(y2**2)*x1*x3+(r**4)+2*(r**2)*(y3**2)+2*(r**2)*(x3**2)+2*(r**2)*(x1**2)-4*(r**2)*x1*x3+(y3**4)+2*(x3**2)*(y3**2)+2*(y3**2)*(x1**2)-4*x1*x3*(y3**2)+(x3**4)+2*(x1**2)*(x3**2)-4*x1*(x3**3)+(x1**4)-4*(x1**3)*x3+4*(x1**2)*(x3**2)-4*(r**2)*(y3**2)-4*(r**2)*(x3**2)+8*x3*x1*(r**2)-4*(x1**2)*(r**2)
        delta=(b**2)-4*a*c
        if delta<0:
            print("bad delta tho")
            return False
        y1_1=(-b-math.sqrt(delta))/(2*a)
        y1_2=(-b+math.sqrt(delta))/(2*a)
        y1=min(y1_1,y1_2)
        R=abs(y2-y1)
        alfa=math.degrees(math.atan2(x3-x1,y3-y1))
        if alfa<0:
            alfa+=360
        circumference_rate=r/R
        return [[x1,y1,R],alfa,circumference_rate]
        
        
    def calculate_line_from_touch_indicator(self, touch_indicator):
        y=self.pos[1]
        x=self.pos[0]
        x1=touch_indicator.pos[0]
        y1=touch_indicator.pos[1]
        r=touch_indicator.size[0]
        a=(y1-y)/(x1-x)
        xr=math.sqrt((r**2)/(a**2+1))+x1
        yr=math.sqrt((r**2)/((1/a)**2+1))+y1
        points = [(x,y),(xr,yr)]
        Line(width=0.04*Metrics.cm,points=points)
        return math.atan(a)

    def draw(self):
        self.canvas.clear()
        if self.fill_rate > 0:
            self.end_point[0]+=self.fill_rate*OrderTracker.FILL_RATE_CONVERSION
        if self.end_point[0]>=WINDOW_WIDTH:
            self.fill_rate=0
        if self.pos==self.end_point:
            return
        with self.canvas:
            Color(self.red,self.green,self.blue)
            points = [self.pos,self.end_point]
            Line(width=0.1*Metrics.cm,points=points)

    def fill(self, fill_rate):
        self.fill_rate=fill_rate
    
    def set_color(self,r,g,b):
        self.red=r
        self.green=g
        self.blue=b

    def implode(self):
        self.is_imploding=True

    def implode_process(self,dt):
        self.pos[0]+=OrderTracker.IMPLODE_RATE*dt
        if self.pos[0]>=WINDOW_WIDTH:
            self.set_color(0,0,0)
            self.pos[0]=WINDOW_WIDTH-1*Metrics.cm
            self.end_point[0]=self.pos[0]
            self.is_imploding=False
        

#dystrybutor eventów
class InputHandler():
    def __init__(self):
        print("ih init")
        self.touch_indicators = {}
        self.blacklist_touches = []
        self.ti_to_remove = []
        self.order_trackers = {}
        self.chosen_indicators = []
        self.root_widget = None
        self.animation=Animation(size=(1*Metrics.cm,1*Metrics.cm),duration=.7)+Animation(size=(0.8*Metrics.cm,0.8*Metrics.cm),duration=.7)
        self.animation.repeat=True
        self.animation_shrink=Animation(size=(0.8*Metrics.cm,0.8*Metrics.cm),duration=.4)
        self.tick_event=None
        self.is_choice_running=False
        self.is_choice_done=False
        self.choice_timer=0
        self.max_trackers=(WINDOW_HEIGHT-2*Metrics.mm)/(5*Metrics.mm)
        self.DEL_TIME_MAX = 5
        self.chosen_deletion_timer = self.DEL_TIME_MAX
        self.is_chosen_deletion_running = False
        self.animation_implode=Animation(size=(1,1),duration=self.DEL_TIME_MAX)
   
    def choice_process(self):
        if self.choice_timer < 120:
            self.choice_timer+=1
        else:
            places = []
            for u in self.touch_indicators:
                places.append(len(places))
            number_places=len(places)
            for ti in self.touch_indicators.values():
                self.chosen_indicators.append(ti)
                place=math.floor(random.random()*len(places))
                ti.choice_display(places.pop(place),number_places)
            self.is_choice_running=False
            self.is_choice_done=True
            

    def on_move(self, event, etype, me):
        if me.is_touch:
            pos = me.to_absolute_pos(me.sx,me.sy,WINDOW_WIDTH,WINDOW_HEIGHT,0)
            if me.uid not in self.blacklist_touches:
                if me.uid not in self.touch_indicators:
                    ti=TouchIndicator(me.uid)
                    self.touch_indicators[me.uid]=ti
                    self.root_widget.add_widget(ti)
                    self.animation.start(ti)
                    self.update_choice_countdown_state()
                if len(self.touch_indicators) > len(self.order_trackers):
                    number=len(self.order_trackers)+1
                    if not number > self.max_trackers:
                        ot=OrderTracker(number)
                        self.order_trackers[number] = ot
                        self.root_widget.add_widget(ot)
                self.touch_indicators[me.uid].pos=pos
        pass

    def on_release(self, event, touch):
        if touch.uid in self.touch_indicators.keys():
            if self.chosen_indicators.count(self.touch_indicators.get(touch.uid)) == 0:
                ti = self.touch_indicators.pop(touch.uid)
                ti.delete()
                input_handler.animation.cancel(ti)
                input_handler.root_widget.remove_widget(ti)
                #if self.chosen_indicators.count(ti) > 0: ###trzeba zrobić usuwanie
                #    self.chosen_indicators.remove(ti)    ###ti już użytych do losowania
            
            else:
                ti = self.touch_indicators.pop(touch.uid)
                self.ti_to_remove.append(ti)
        elif touch.uid in self.blacklist_touches:
            self.blacklist_touches.remove(touch.uid)
            
    def check_if_any_chosen(self):
        if len(self.chosen_indicators) > 0:
            return True
        return False

    def chosen_deletion_countdown_start(self):
        self.is_chosen_deletion_running=True
        for ti in self.chosen_indicators:
            print("buujaa")
            Animation.cancel_all(ti) #Animacja jest jak zabiorę nowe kółko, ale nie ma jak zostawię
            self.animation_implode.start(ti)
            
    def is_in_iterable(self, iterable, thing):
        for i in iterable:
            if i == thing:
                return True
        return False
    
    def chosen_deletion_countdown(self, dt):
        self.chosen_deletion_timer-=dt
        print(self.chosen_deletion_timer)
        if self.chosen_deletion_timer <=0:
            for ti in self.chosen_indicators:
                ti.delete()
                self.animation.cancel(ti)
                self.root_widget.remove_widget(ti)
                if self.is_in_iterable(self.touch_indicators.keys(),ti.touch_id):
                    self.touch_indicators.pop(ti.touch_id)
                    self.blacklist_touches.append(ti.touch_id)
                if self.ti_to_remove.count(ti) > 0:
                    self.ti_to_remove.remove(ti) 
                self.chosen_indicators.remove(ti)
            for ot in self.order_trackers.values():
                ot.implode()
            if len(self.chosen_indicators)==0:
                self.chosen_deletion_countdown_reset()
                self.update_choice_countdown_state()

    def chosen_deletion_countdown_reset(self):
        self.chosen_deletion_timer=self.DEL_TIME_MAX
        self.is_chosen_deletion_running = False
        for ti in self.chosen_indicators:
            Animation.cancel_all(ti)
            self.animation_shrink.start(ti)

    def update_choice_countdown_state(self):
        if len(self.touch_indicators) >= 2 and not len(self.chosen_indicators) > 0:
                    self.is_choice_running = True
                    self.choice_timer=0
        else:
            self.is_choice_running=False
            
        
#main
class MyApp(App):
    def build(self):
        Window.bind(on_motion=input_handler.on_move)
        Window.bind(on_touch_up=input_handler.on_release)
        widget=Widget(width=WINDOW_WIDTH,height=WINDOW_HEIGHT)
        input_handler.root_widget=widget
        input_handler.tick_event=Clock.schedule_interval(self.frametick,1/Config.getint('graphics','maxfps'))
        return widget
    def frametick(self,dt):
        #print(len(input_handler.chosen_indicators))
        #print(len(input_handler.touch_indicators))
        #print(len(input_handler.ti_to_remove))
        #print()
        #print(Clock.get_fps())
        self.update_chosen_deletion()
        if input_handler.is_chosen_deletion_running:
            input_handler.chosen_deletion_countdown(dt)
        for ti in input_handler.touch_indicators.values():
            ti.outline_animation_fill(dt,360,200)
            ti.outline_animation_drain(dt,720)
            ti.circle()
        for ti in input_handler.ti_to_remove:
            ti.outline_animation_fill(dt,360,200)
            ti.outline_animation_drain(dt,720)
            ti.circle()
            if ti.is_drain_running==False:
                pass
        for ot in input_handler.order_trackers.values():
            ot.draw()
            if ot.is_imploding:
                ot.implode_process(dt)
        if input_handler.is_choice_running:
            input_handler.choice_process()

            
    def update_chosen_deletion(self):
        if input_handler.check_if_any_chosen():
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
#TODO: animacje obwódki idące w dół jak muszą
#usuwanie z pamięci obiektów jak zakończą swoje animacje
