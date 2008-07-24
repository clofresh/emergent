from gui import Paintable, Updateable
from pygame import draw, Rect
from pygame.constants import *
from behaviors import *
from sets import Set
from random import randint
from common import RESOLUTION

class Entity(Paintable, Updateable):
    entityBehaviors = {}

    def __init__(self, world, family = None, position = None):
        if position == None:
            offset = (int(RESOLUTION[0]/5), int(RESOLUTION[1]/5))
#            position = (randint(offset[0], RESOLUTION[0] - offset[0]), randint(offset[1], RESOLUTION[1] - offset[1]))
            position = map(lambda offset, resolution: randint(offset, resolution - offset), offset, RESOLUTION)
    
        Paintable.__init__(self, position)
        self.boundingBox = Rect(position, self.getInitialDimensions())
        self.age = 0
        self.health = self.getAttribute('health')
        self.growthFactor = self.getAttribute('growthFactor')
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

    def __del__(self):
#        print 'Destructing ', self
        
        for base in self.__class__.__bases__:
            # Avoid problems with diamond inheritance.
            basekey = 'del_' + str(base)
            if not hasattr(self, basekey):
                setattr(self, basekey, 1)
            else:
                continue
            # Call this base class' destructor if it has one.
            if hasattr(base, "__del__"):
                base.__del__(self)

    def getId(self):
        return self.getSpecies()
        
    def getSpecies(self):
        return self.__class__.__name__
        
    def getFamily(self):
        return self.family
    
    def getBoundingBox(self):
        return self.boundingBox

    def getDimensions(self):
        return [self.boundingBox.w, self.boundingBox.h]

    def getPosition(self):
        return self.boundingBox.center
        
    def getCarriedEntity(self):
        return self.carriedEntity
        
    def isCarryingEntity(self, type = None):
        if type:
            return self.carriedEntity.__class__ == type
        else:
            return self.carriedEntity != None
    
    def isCarried(self):
        return self.beingCarried

    def getAttribute(self, attributeName):
        attribute = self.__class__.attributes[attributeName]
        if attribute.__class__.__name__ == 'function':
            return attribute()
        else:
            return attribute

    def getInitialHealth(self):
        return self.getAttribute('health')

    def getInitialDimensions(self):
        return self.getAttribute('dimensions')
    
    def getColor(self):
        return self.getAttribute('color')

    def getGrowthFactor(self):
        return self.growthFactor

    def getHealth(self):
        return self.health
        
    def getAge(self):
        return self.age

    def paint(self, screen):
        draw.rect(screen, self.getColor(), self.boundingBox)
        
    def update(self, delay, world):
        if self.__class__.entityBehaviors:
            for behavior, params in self.__class__.entityBehaviors.iteritems():
                extraParams = [self, world]
                extraParams.extend(params)
                behavior.do(extraParams)
                
        self.age += 1
        
    def grow(self, growthArea):
        growthFactor = self.getGrowthFactor()
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
#        return self.behavior.hasBehavior(behavior)
        pass
    
    def addBehavior(self, behavior):
#        self.behavior.add(behavior)
        pass
    
    def removeBehavior(self, behavior):
#        self.behavior.removeBehavior(behavior)
        pass
    
    def __str__(self):
        return '%s (%s, %s)' % (self.__class__.__name__, self.boundingBox.x, self.boundingBox.y)

class Family(Entity):
    nextId = 0

    def __init__(self, world, name = 'Family'):
        self.id = self.getNextId()
        self.memberCount = {}
        self.boundingBox = None
#        world.register(self)

    def getFamily(self):
        return self

    def getNextId(self):
        Family.nextId += 1
        return Family.nextId
    
    def getId(self):
        return self.__class__.__name__ + str(self.id)
    
    def __cmp__(self, other):
        return cmp(self.getId(), other.getId())

    def __hash__(self):
        return self.id
            
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
            box = member.getBoundingBox()
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
        
    def getInitialHealth(self):
        return 1000

    def getInitialDimensions(self):
        return (3,3)
    
    def getColor(self):
        return (200, 0, 0)

class FoodFamily(Family):
    def paint(self, screen):
        pass
        
    def update(self, delay, world):
        pass

class Food(Entity):
    def __init__(self, world, family = None, position = None):
        if position == None:
            position = (randint(100,540), randint(100,380))

        self.boundingBox = Rect(position, self.getInitialDimensions())
        if not family:
            family = FoodFamily(world)
        Entity.__init__(self, world, family, position)

    def feed(self, eater):
        dimensions = self.getDimensions()
        eater.grow(dimensions)
        self.grow(map(lambda x: -1*x, dimensions))
        self.health -= 100*eater.getGrowthFactor()



Drone.entityBehaviors = {EntityBehavior(RandomMove)   : [],                                     \
                       EntityBehavior(ApproachFamily) : [0.50, 50, False, [Queen]],             \
                       EntityBehavior(Mutate)         : [1.00, {Hunter: .001, Queen: .0005}],   \
                       EntityBehavior(Decay)          : [1.00, 80],                             \
                       EntityBehavior(StartNewFamily) : [0.01],                                 \
                       EntityBehavior(Eat)            : [.50],                                  \
                       EntityBehavior(Gather)         : [.50, 100, [Food]]                      \
                       }

Drone.attributes = {'health'         : lambda:randint(200,400),                                 \
                    'dimensions'    : (5, 5),                                                   \
                    'color'         : (0, 0, 200),                                              \
                    'growthFactor'  : 0.25                                                      \
                    }

Queen.entityBehaviors = {EntityBehavior(RandomMove)   : [],                                     \
                       EntityBehavior(ApproachFamily) : [0.50, 200, False, [Drone]],            \
                       EntityBehavior(Mate)           : [0.10],                                 \
                       EntityBehavior(Decay)          : [1.00, 125],                            \
                       EntityBehavior(Absorb)         : [1.00, [Queen]],                        \
                       EntityBehavior(StartNewFamily) : [0.01]                                  \
                       }

Queen.attributes = {'health'        : lambda:randint(500,1000),                                 \
                    'dimensions'    : lambda:[randint(6,10)]*2,                                 \
                    'color'         : (0, 200, 0),                                              \
                    'growthFactor'  : 0.25                                                      \
                    }

Hunter.entityBehaviors = {EntityBehavior(Absorb)      : [],                                     \
                       EntityBehavior(ApproachFamily) : [0.75, 50, False],                      \
                       EntityBehavior(Mutate)         : [1.00, {Queen: .0005}],                 \
                       EntityBehavior(Explode)        : [1.00, 20],                             \
                       EntityBehavior(StartNewFamily) : [0.01]                                  \
                       }

Hunter.attributes = {'health'        : lambda:randint(500,1000),                                \
                    'dimensions'    : (3,3),                                                    \
                    'color'         : (200, 0, 0),                                              \
                    'growthFactor'  : 0.25                                                      \
                    }

Food.entityBehaviors = {EntityBehavior(Multiply)      : [0.005, 3, 5],                          \
                        EntityBehavior(Decay)          : [1.00, 1000],                           \
                        }

Food.attributes = {'health'        : lambda:randint(100,300),                                   \
                   'dimensions'    : lambda:[randint(2,10)]*2,                     \
                   'color'         : (133, 88, 10),                                             \
                   'growthFactor'  : 0.25                                                       \
                    }





def familyHasQueen(family):
    return False
    return family.memberCount(Queen) > 0

