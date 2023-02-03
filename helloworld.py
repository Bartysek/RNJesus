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
    def __init__(self):
        super().__init__()
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
        #print(angle_start)
        #print(arch_angle)
        #print("")
   
    def outline_instructions(self):
        for segment in self.segments:
                self.outline_segment(segment[0],segment[1])
        #if self.arch_angle==360:
        #    Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0]))
        #if self.end_angle()>self.start_angle:
        #    Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0],self.start_angle,self.end_angle()))
        #else:
        #    Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0],self.start_angle,360))           
        #    Line(width=0.04*Metrics.cm,cap='round',circle=(self.pos[0],self.pos[1],self.size[0],0,self.end_angle()))            

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
            encircle_info=input_handler.order_trackers.get(self.number).calculate_circle_from_touch_indicator(self)
            self.draining_angle=encircle_info[1]
        self.drained_angle=self.set_general_angle_restricted(dt*drain_rate+self.drained_angle)
        self.set_start_angle(self.draining_angle+self.drained_angle)
        self.set_arch_angle(360-self.drained_angle)
        if self.number <= input_handler.max_trackers:
            if self.segments[0][1]==0:
                self.drain_move_seconds+=dt
            circum_rate=encircle_info[2]
            move_rate_encircle=drain_rate*circum_rate
            arch_angle_encircle=self.set_general_angle_restricted(self.drained_angle*circum_rate)
            start_angle_encircle=self.set_general_angle_restricted(encircle_info[1]+move_rate_encircle*self.drain_move_seconds)
            end_angle_encircle=self.set_general_angle_restricted(start_angle_encircle+arch_angle_encircle)
            print(start_angle_encircle)
            print(end_angle_encircle)
            print()
            encircle = encircle_info[0]
            encircle.append(start_angle_encircle)
            encircle.append(end_angle_encircle)
            self.encircle=encircle
            if end_angle_encircle==360:
                input_handler.order_trackers.get(self.number).fill(drain_rate)
            if start_angle_encircle==360:
                self.is_drain_running = False
                return True
            
            
    def circle(self):
        self.canvas.clear()
        with self.canvas:
            Color(self.red,self.green,self.blue)
            Circle(self.pos,0.75*self.size[0])
            #Color(1.,.5,0,.5)
            #Line(width=0.02*Metrics.cm,circle=(self.pos[0],self.pos[1],0.75*self.size[0]+1))
            self.outline_instructions()
            #encircle_info=input_handler.order_trackers.get(1).calculate_circle_from_touch_indicator(self)
            #encircle=encircle_info[0]
            #if encircle:
            #    arc=encircle_info[1]
            #    if arc<0:
            #        arc=360+arc
            #    self.drain_angle_start=arc
            #    encircle_=(encircle[0],encircle[1],encircle[2],arc,360)
            #    Line(circle=encircle_,width=2)
            if self.is_drain_running and self.is_connected_to_order_tracker():
                Line(width=0.04*Metrics.cm,circle=self.encircle)
            if self.number:
                Color(0,0,0)
                Numbers.method(self.number)(0.6*self.size[0],self.pos,self.number)
                
        
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
        
        self.fill_rate=0

    FILL_RATE_CONVERSION=Metrics.mm/5000

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
        if self.end_point[0]==WINDOW_WIDTH:
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
        
        

#dystrybutor eventów
class InputHandler():
    def __init__(self):
        print("ih init")
        self.touch_indicators = {}
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
            if me.uid not in self.touch_indicators:
                ti=TouchIndicator()
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
        if self.chosen_indicators.count(self.touch_indicators.get(touch.uid)) == 0:
            ti = self.touch_indicators.pop(touch.uid)
            self.ti_to_remove.append(ti)
            #if self.chosen_indicators.count(ti) > 0: ###trzeba zrobić usuwanie
            #    self.chosen_indicators.remove(ti)       ti już użytych do losowania
            
        else:
            self.touch_indicators.pop(touch.uid)
            

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
        #with widget.canvas:
        #    Color(1.,1.,0)
        #    Rectangle(size=(widget.width,widget.height),pos=widget.pos)
        return widget
    def frametick(self,dt):
        print(Clock.get_fps())
        for ti in input_handler.touch_indicators.values():
            ti.outline_animation_fill(dt,360,200)
            ti.outline_animation_drain(dt,720)
            ti.circle()
        for ti in input_handler.ti_to_remove:
            ti.outline_animation_fill(dt,360,200)
            ti.outline_animation_drain(dt,720)
            ti.circle()
            if ti.is_drain_running==False:
                self.update_choice_countdown_state()
                ti.delete()
                self.animation.cancel(ti)
                self.root_widget.remove_widget(ti)
        for ot in input_handler.order_trackers.values():
            ot.draw()
        if input_handler.is_choice_running:
            input_handler.choice_process()
                
Numbers = vertex.numbers.Numbers()
input_handler = InputHandler()
MyApp().run()
#TODO: animacje obwódki idące w dół jak muszą
#usuwanie z pamięci obiektów jak zakończą swoje animacje
