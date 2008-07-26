from common import SubclassShouldImplement
from pygame.constants import *
 
class Paintable:
    """loc is a tuple of the upper-left location to paint this paintable at.
    Subclasses (such as Mouseable) depend on the first two entries being x,y"""
    def __init__(self, loc=None):
        self.loc = loc
    
    def paint(self,screen):
	   raise SubclassShouldImplement
    
class Mouseable(Paintable):
    """bounds is the location and width/height of the mouseable.  If None,
    we're everywhere!"""
    
    def __init__(self,bounds = None):
        Paintable.__init__(self,bounds)
        self.buttonState = MOUSEBUTTONUP
        
    def mouseEvent(self,event):
        "event is a MOUSE* event, this routine decodes it and calls one of the subs"
        x,y = event.pos
        if event.type == MOUSEBUTTONDOWN:
            self.buttonState = event.type
            self.mouseDownEvent(x,y)
        elif event.type == MOUSEBUTTONUP:
            self.buttonState = event.type
            self.mouseUpEvent(x,y)
        elif event.type == MOUSEMOTION:
            if self.buttonState == MOUSEBUTTONDOWN:
                self.mouseDragEvent(x,y)
            self.mouseMoveEvent(x,y)
    
    def mouseDownEvent(self,x,y):
        pass
        
    def mouseUpEvent(self,x,y):
        pass
        
    def mouseDragEvent(self,x,y):
        pass
        
    def mouseMoveEvent(self,x,y): 
        pass
        
class Keyable:
    def __init__(self, keys=None):
        """keys is a list of keys that this will respond to.  If None, it listens
     to everything"""
        self.keys = keys
        
    def maskEvent(self, key, unicode, pressed):
        if self.keys:
                if not (key in self.keys):
                    return
        self.keyEvent(key,unicode,pressed)
        
    def keyEvent(self,key,unicode, pressed):
        raise SubclassShouldImplement
    
class Updateable:
 
    def update(self,delay):
        "delay is the time in seconds passed since last iteration"
        raise SubclassShouldImplement
