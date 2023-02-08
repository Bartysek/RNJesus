from kivy.graphics import *
import math

SIZE_MULTIPLIER=1/8

class Numbers():
    def method(self,number):
        if number < 0:
            return self.null
        if number==0:
            return self.zero
        if number==1:
            return self.one
        if number==2:
            return self.two
        if number==3:
            return self.three
        if number==4:
            return self.four
        if number==5:
            return self.five
        if number==6:
            return self.six
        if number==7:
            return self.seven
        if number==8:
            return self.eight
        if number==9:
            return self.nine
        else:
            return self.double_digit
    def null(self,size=0,pos=0,number=0):
        pass

    def zero(self,size=0,pos=(0,0),number=0):
        width=size*SIZE_MULTIPLIER
        Line(ellipse=(pos[0]-size/4,pos[1]-size/2,size/2,size),width=width)
    
    def one(self,size=0, pos=(0,0),number=0):
        points = []
        points.append((pos[0],pos[1]-size/2))
        points.append((pos[0],pos[1]+size/2))
        points.append((pos[0]-size/2.8,pos[1]+size/4.8))
        width=size*SIZE_MULTIPLIER
        Line(points=points,width=width)

    def two(self,size=0, pos=(0,0),number=0):
        points = []
        points.append((pos[0]+size/4,pos[1]-size/2))
        points.append((pos[0]-size/4,pos[1]-size/2))
        points.append((pos[0]+size/4,pos[1]+size/4))
        width=size*SIZE_MULTIPLIER
        Line(points=points,width=width)
        Line(circle=(pos[0],pos[1]+size/4,size/4,270,360),width=width)
        Line(circle=(pos[0],pos[1]+size/4,size/4,0,90),width=width)

    def three(self,size=0, pos=(0,0),number=0):
        width=size*SIZE_MULTIPLIER
        Line(circle=(pos[0],pos[1]+size/4,size/4,320,360),width=width)
        Line(circle=(pos[0],pos[1]+size/4,size/4,0,180),width=width)
        Line(circle=(pos[0],pos[1]-size/4,size/4,0,220),width=width)

    def four(self,size=0, pos=(0,0),number=0):
        points = []
        points.append((pos[0]+size/4,pos[1]-size/5))
        points.append((pos[0]-size/4,pos[1]-size/5))
        points.append((pos[0]-size/5,pos[1]+size/2))
        points2 = []
        points2.append((pos[0]+size/10,pos[1]))
        points2.append((pos[0]+size/10,pos[1]-size/2))
        width=size*SIZE_MULTIPLIER
        Line(points=points,width=width)
        Line(points=points2,width=width)

    def five(self,size=0, pos=(0,0),number=0):
        points = []
        points.append((pos[0]+size/4,pos[1]+size/2))
        points.append((pos[0]-size/4,pos[1]+size/2))
        points.append((pos[0]-size/4,pos[1]+size/8))
        width=size*SIZE_MULTIPLIER
        bezier = []
        bezier.append(pos[0]-size/4)
        bezier.append(pos[1]+size/8)
        bezier.append(pos[0]+size/2.7)
        bezier.append(pos[1]+size/8-size/20)
        bezier.append(pos[0]+size/2.7)
        bezier.append(pos[1]-size/2)
        bezier.append(pos[0]-size/4+size/50)
        bezier.append(pos[1]-size/2)
        Line(points=points, width=width)
        Line(width=width,bezier=bezier)

    def six(self,size=0, pos=(0,0),number=0):
        width=size*SIZE_MULTIPLIER
        points = []
        points.append((pos[0]-size/4,pos[1]-size/4))
        points.append((pos[0]-size/4,pos[1]+size/4))
        Line(width=width, points=points)
        Line(width=width, circle=(pos[0],pos[1]-size/4,size/4))
        Line(width=width, circle=(pos[0],pos[1]+size/4,size/4,270,360))
        Line(width=width, circle=(pos[0],pos[1]+size/4,size/4,0,60))

    def seven(self,size=0, pos=(0,0),number=0):
        width=size*SIZE_MULTIPLIER
        points = []
        points.append((pos[0]-size/4,pos[1]+size/2))
        points.append((pos[0]+size/4,pos[1]+size/2))
        points.append((pos[0]-size/5,pos[1]-size/2))
        Line(width=width,points=points)

    def eight(self,size=0, pos=(0,0),number=0):        
        width=size*SIZE_MULTIPLIER
        Line(width=width,circle=(pos[0],pos[1]+size/4,size/4))
        Line(width=width,circle=(pos[0],pos[1]-size/4,size/4))
    
    def nine(self,size=0, pos=(0,0),number=0):
        width=size*SIZE_MULTIPLIER
        points = []
        points.append((pos[0]+size/4,pos[1]-size/4))
        points.append((pos[0]+size/4,pos[1]+size/4))
        Line(width=width, points=points)
        Line(width=width, circle=(pos[0],pos[1]+size/4,size/4))
        Line(width=width, circle=(pos[0],pos[1]-size/4,size/4,90,240))

    def double_digit(self,size=0,pos=(0,0),number=0):
        digit_1=max(math.floor(number/10),1)
        digit_2=number-(10*digit_1)
        if digit_1 not in range(10):
            print("co jest nie tak")
            return
        if digit_2 not in range(10):
            print("co jest nie tak2")
            return
        self.method(digit_1)(size,pos=(pos[0]-size/3,pos[1]),number=1)
        self.method(digit_2)(size,pos=(pos[0]+size/3,pos[1]),number=1)
        
        
        
