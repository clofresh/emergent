from random import randint
from types import FunctionType

from pygame import draw, Rect
from pygame.constants import *

from common import RESOLUTION
from gui import Paintable, Updateable

class Genotype(object):
    def __init__(self, health=1, dimensions=(1,1), color=(0,0,0), growthFactor=0.0):
        self.__health = health
        self.__dimensions = dimensions
        self.__color = color
        self.__growthFactor = growthFactor

    def getHealth(self):
        if isinstance(self.__health, FunctionType):
            return self.__health()
        else:
            return self.__health
    
    def getDimensions(self):
        if isinstance(self.__dimensions, FunctionType):
            return self.__dimensions()
        else:
            return self.__dimensions
    
    def getColor(self):
        if isinstance(self.__color, FunctionType):
            return self.__color()
        else:
            return self.__color
    
    def getGrowthFactor(self):
        if isinstance(self.__growthFactor, FunctionType):
            return self.__growthFactor()
        else:
            return self.__growthFactor
    
    health       = property(getHealth)
    dimensions   = property(getDimensions)
    color        = property(getColor)
    growthFactor = property(getGrowthFactor)

class Personality(object):
    def __init__(self, behavior_list=[]):
        self.behaviors = set(behavior_list)
    
    def __iter__(self):
        for behavior in self.behaviors:
            yield behavior

class Entity(Paintable, Updateable):
    entityBehaviors = Personality()
    attributes = Genotype()

    def __init__(self, world, family = None, position = None):
        if position == None:
            offsets = (int(dimension/5.0) for dimension in RESOLUTION)

            position = tuple(randint(offset, dimension - offset) 
                             for offset, dimension 
                             in zip(offsets, RESOLUTION))
    
        Paintable.__init__(self, position)
        self.boundingBox = Rect(position, self.attributes.dimensions)
        
        self.age = 0
        self.health = self.attributes.health
        self.growthFactor = self.attributes.growthFactor
        self.carriedEntity = None
        self.beingCarried = False

        if family:
            self.family = family
        else:
            self.family = Family(world)
            self.family.boundingBox = self.boundingBox
            
#        self.family.addMember(self)

#        self.behavior = ComplexBehavior(self, world)
        world.register(self)

    def getSpecies(self):
        return self.__class__.__name__
        
    def getFamily(self):
        return self.family
    
    def getDimensions(self):
        return [self.boundingBox.w, self.boundingBox.h]

    def getPosition(self):
        return self.boundingBox.center
    
    def getStride(self):
        return round(self.getDimensions()[0] / 2.)
        
    def isCarryingEntity(self, type = None):
        if type:
            return self.carriedEntity.__class__ == type
        else:
            return self.carriedEntity != None
    
    def paint(self, screen):
        draw.rect(screen, self.attributes.color, self.boundingBox)
        
    def update(self, delay, world):
        if self.__class__.entityBehaviors:
            for behavior in self.__class__.entityBehaviors:
                behavior.do(self, world)
                
        self.age += 1
        
    def grow(self, growthArea):
        growthFactor = self.growthFactor
        self.boundingBox.inflate_ip(growthArea[0] * growthFactor, growthArea[1] * growthFactor)
        gain = growthArea[0]  * growthArea[1]
#        print 'Gained %s health' % gain
        self.health += gain

    def carryEntity(self, entity):
        entity.beingCarried = True
        self.carriedEntity = entity
        
    def dropEntity(self):
        if self.carriedEntity:
            self.carriedEntity.beingCarried = False
            self.carriedEntity = None

    def hasBehavior(self, behavior):
        return self.behavior in behavior
    
    def addBehavior(self, behavior):
#        self.behavior.add(behavior)
        pass
    
    def removeBehavior(self, behavior):
#        self.behavior.removeBehavior(behavior)
        pass
    
    def __str__(self):
        return '%s (%s, %s)' % (self.__class__.__name__, self.boundingBox.x, self.boundingBox.y)

class Family(Entity):
    def __init__(self, world, name = 'Family'):
        self.memberCount = {}
        self.boundingBox = None
#        world.register(self)

    def getFamily(self):
        return self

    def __cmp__(self, other):
        return cmp(id(self), id(other))

    def __hash__(self):
        return id(self)
            
    def getTerritoryRadius(self):
        return max(self.boundingBox.w, self.boundingBox.h)/2

    def getMemberCount(self, memberType = None):
        if self.memberCount:
            if memberType:
                try:
                    count = self.memberCount[memberType]
                except KeyError:
                    count = 0
            else:
                count = reduce(lambda total, typeCount: total+typeCount, self.memberCount.values(), 0)
        else:
            count = 0

        return count
    
    def addMember(self, entity):
        self.members.add(entity)
        return self
        
    def removeMember(self, entity, world):
        self.members.discard(entity)
        if self.memberCount() == 0:
            print 'The %s bloodline ended' % self
            world.unregister(self)
        return self
        
    def isMember(self, entity):
        return entity in self.members
        
    def isAlliedMember(self, entity):
        for family in self.allies:
            if family.isMember(entity):
                return True
        return False
        
    def allyWith(self, newFamily):
        self.allies.add(newFamily)
        
    def addBehavior(self, behavior):
        for member in self.members:
            member.addBehavior(behavior)

    def removeBehavior(self, behavior):
        for member in self.members:
            member.removeBehavior(behavior)

    def paint(self, screen):
        radius = self.getTerritoryRadius()
        if self.getMemberCount() > 1 and radius > 2:
            draw.circle(screen, (10,20,30), self.boundingBox.center, radius, 2)
        
    def update(self, delay, world):
        def findEdges(currentEdges, member):
            left, top, right, bottom = currentEdges
            box = member.boundingBox
            currentEdges = [min(left, box.left), min(top, box.top), max(right, box.right), max(bottom, box.bottom)]
            
            try:
                self.memberCount[member.__class__] += 1
            except KeyError: 
                self.memberCount[member.__class__] = 1
                            
            return currentEdges

        self.memberCount = {}
        left, top, right, bottom = reduce(findEdges, world.getFamilyMembers(self), [RESOLUTION[0], RESOLUTION[1], 0, 0])

        dimensions = (right - left,  bottom - top)
        
        self.boundingBox = Rect((left, top), dimensions)

                

class Drone(Entity):
    def __init__(self, world, family = None, position = None):
        Entity.__init__(self, world, family, position)

class Queen(Entity):
    def __init__(self, world, family = None, position = None):
        Entity.__init__(self, world, family, position)
        
class Hunter(Entity):
    def __init__(self, world, family = None, position = None):
        Entity.__init__(self, world, family, position)
#        self.behavior.add(StartNewFamily(self, world))
        
class FoodFamily(Family):
    def paint(self, screen):
        pass
        
    def update(self, delay, world):
        pass

class Food(Entity):
    def __init__(self, world, family = None, position = None):
        if position == None:
            position = (randint(100,540), randint(100,380))

        self.boundingBox = Rect(position, self.attributes.dimensions)
        if not family:
            family = FoodFamily(world)
        Entity.__init__(self, world, family, position)

    def feed(self, eater):
        dimensions = self.getDimensions()
        eater.grow(dimensions)
        self.grow(map(lambda x: -1*x, dimensions))
        self.health -= 100*eater.growthFactor







