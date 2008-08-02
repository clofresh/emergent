from math import sqrt
from random import randint

RESOLUTION = (640, 480)
FPS = 60

THREAD_LIMIT = 1

class SubclassShouldImplement(Exception):
    def __init__(self, msg="A method was called which should have been overridden"):
	Exception.__init__(self,msg)

def getDisplacement(box1, box2):
    p1 = box1.center
    p2 = box2.center
    
    return [p2[0] - p1[0], p2[1] - p1[1]]

def getMagnitude(vector):
    mag = 0
    for n in vector:
        mag += pow(n, 2)
        
    return sqrt(mag)

def normalize(vector):
    mag = getMagnitude(vector)
    
    if mag == 0:
        return vector
    
    for i in range(len(vector)):
        vector[i] /= mag
        
    return vector
    
def randomizePosition(position, variance):
    return map(lambda x: x + randint(-1 * variance, variance), position)