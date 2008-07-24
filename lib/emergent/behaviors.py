from common import *
from random import randint, random, choice
import math
from math import exp, log, atan
import entities
from pygame import Rect



class Behavior:
    def __init__(self, doer, world, chanceOfAction = 1.00):
        self.doer = doer
        self.world = world
        self.chanceOfAction = chanceOfAction
        

    def getChanceOfAction(self):
        return self.chanceOfAction

    def setChanceOfAction(self, chance):
        self.chanceOfAction = chance
        return self

    def shouldExecuteBehavior(self):
        return self.getChanceOfAction() > random()

    def do(self):
        raise SubclassShouldImplement

class EntityBehavior:
    def __init__(self, behavior):
        self.behavior = behavior
    
    def do(self, params = []):
        self.behavior(*params).do()

class ComplexBehavior(Behavior):
    def __init__(self, doer, world, chanceOfAction = 1.00):
        Behavior.__init__(self, doer, world, chanceOfAction)
        self.behaviors = []
        
    def add(self, toAdd):
        self.remove(toAdd)
        self.behaviors.append(toAdd)

        
    def remove(self, toRemove):
        try:
            self.behaviors.remove(toAdd)
        except:
            pass
        
    def hasBehavior(self, behavior):
        def getBehaviorClass(b):
            return b.__class__.__name__
        behaviorClasses = map(getBehaviorClass, self.behaviors)
        
        if type(behavior).__name__ == 'classobj':
            behavior = behavior.__name__
        
        return behavior in behaviorClasses
        
    def removeBehavior(self, behavior):
        if type(behavior).__name__ == 'classobj':
            behavior = behavior.__name__

        def filterBehaviors(b):
            return b.__class__.__name__ != behavior
                
        self.behaviors = filter(filterBehaviors, self.behaviors)       
        
    def do(self):
        for b in self.behaviors:
            b.do()
        

class Move(Behavior):
    def __init__(self, doer, world, chanceOfAction = 1.00, displacement = (0, 0)):
        Behavior.__init__(self, doer, world, chanceOfAction)
        self.displacement = displacement
        
    def do(self):
        box = self.doer.getBoundingBox()
        newBox = box.move(self.displacement[0], self.displacement[1])
        self.doer.boundingBox = Rect(newBox.left%RESOLUTION[0], newBox.top%RESOLUTION[1], newBox.w, newBox.h)

        carriedEntity = self.doer.getCarriedEntity()
        if carriedEntity:
            carriedEntityBox = carriedEntity.getBoundingBox()
            newCarriedEntityBox = carriedEntityBox.move(self.displacement[0], self.displacement[1])
            self.doer.getCarriedEntity().boundingBox = Rect(newCarriedEntityBox.left%RESOLUTION[0], newCarriedEntityBox.top%RESOLUTION[1], newCarriedEntityBox.w, newCarriedEntityBox.h)
        
        
        
class RandomMove(Move):
    def __init__(self, doer, world, chanceOfAction = 1.00):
        Move.__init__(self, doer, world, chanceOfAction)

    def do(self):
        stride = round(self.doer.getDimensions()[0] / 2)
    
        dx = randint(-1 * stride, stride)
        dy = randint(-1 * stride, stride)
        self.displacement = (dx, dy)
        return Move.do(self)

class Sense(Behavior):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None):
        Behavior.__init__(self, doer, world, chanceOfAction)
        self.world = world
        if senseDistance:
            self.senseDistance = senseDistance
        else:
            self.senseDistance = self.doer.getDimensions()[0] + 1

    def updateSenseDistance(self):
        pass
    
    def senseAction(self, inRange):
        pass

    def othersInRange(self):
        self.updateSenseDistance()
        senseBox = self.doer.getBoundingBox().inflate(self.senseDistance, self.senseDistance)
        return self.world.checkNeighbors(self.doer, senseBox)

    def filterTargets(self, possibleTargets, targetEntities):
        if possibleTargets and targetEntities:    
            def filterEntities(e):
                return e.__class__ in targetEntities
            possibleTargets = filter(filterEntities, possibleTargets)
        return possibleTargets
        

    def doToWithinRange(self, func = None):
        if func == None:
            func = self.senseAction
            
        inRange = self.othersInRange()
        if inRange and self.shouldExecuteBehavior():
            func(inRange)
            return True
        else:
            return False

    def do(self):
        self.doToWithinRange(self.senseAction)

class SenseFamilial(Sense):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None, senseFamily = True):
        Sense.__init__(self, doer, world, chanceOfAction, senseDistance)
        self.senseFamily = senseFamily

    def othersInRange(self):
        def familial(e):
            if self.senseFamily:
                return e.getFamily() == self.doer.getFamily()
            else:
                return e.getFamily() != self.doer.getFamily()

        inRange = Sense.othersInRange(self)
        return filter(familial, inRange)

        
class Response(Move, Sense):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None):
        Move.__init__(self, doer, world, chanceOfAction)
        Sense.__init__(self, doer, world, chanceOfAction, senseDistance)

class Approach(Response):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None, toApproach = []):
        Response.__init__(self, doer, world, chanceOfAction, senseDistance)
        self.randomMove = RandomMove(self.doer, world)
        self.toApproach = toApproach

    def othersInRange(self):
        return self.filterTargets(Response.othersInRange(self), self.toApproach)        

    def senseAction(self, inSight):
        toApproach = inSight[0]
#            print 'Found %s' % toApproach
        self.displacement = normalize(getDisplacement(self.doer.getBoundingBox(), toApproach.getBoundingBox()))

        if self.displacement[0] == 0 and self.displacement[1] == 0:
            self.randomMove.do()
        else:
            self.displacement[0] = round(self.displacement[0] * 2)
            self.displacement[1] = round(self.displacement[1] * 2)

            Move.do(self)

    def do(self):
        if self.doToWithinRange() == False:
            self.randomMove.do()

class ApproachFamily(Approach, SenseFamilial):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None, senseFamily = True, toApproach = []):
        SenseFamilial.__init__(self, doer, world, chanceOfAction, senseDistance, senseFamily)
        Approach.__init__(self, doer, world, chanceOfAction, senseDistance, toApproach)

    def othersInRange(self):
        return self.filterTargets(SenseFamilial.othersInRange(self), self.toApproach)        
        

class Avoid(Response):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None, toAvoid = []):
        Response.__init__(self, doer, world, chanceOfAction, senseDistance)
        self.toAvoid = toAvoid
        
    def senseAction(self, inSight):
        # take the average vector of all the things to avoid within sight range 
        pass

class Absorb(SenseFamilial):
    def __init__(self, doer, world, chanceOfAction = 1.00, toAbsorb = []):
        SenseFamilial.__init__(self, doer, world, chanceOfAction, None, False)
        self.toAbsorb = toAbsorb
        self.chanceOfAction = .1
        
    def updateSenseDistance(self):
        self.senseDistance = self.doer.getDimensions()[0] + 1

    def othersInRange(self):
        return self.filterTargets(SenseFamilial.othersInRange(self), self.toAbsorb)        

    def senseAction(self, inRange):
        for e in inRange:
            self.doer.grow(e.getDimensions())
            self.world.unregister(e)
            
class Eat(Sense):
    def othersInRange(self):
        return self.filterTargets(Sense.othersInRange(self), [entities.Food])

    def senseAction(self, edibles):
        toEat = edibles[0]
        toEat.feed(self.doer)
#        print '%s is eating %s' % (self.doer, toEat)
        
class Carry(Sense):
    def othersInRange(self):
        return self.filterTargets(Sense.othersInRange(self), [entities.Food])

    def senseAction(self, inRange):
        if self.doer.isCarryingEntity():
#            print 'Dropping', self.doer.getCarriedEntity()
            self.doer.dropEntity()
        else:
            for e in inRange:
                if not e.isCarried():
                    self.doer.carryEntity(e)
                    break

#            print 'Picking up', self.doer.getCarriedEntity()

class Gather(ComplexBehavior):
    def __init__(self, doer, world, chanceOfAction = 1.00, senseDistance = None, toGather = []):
        ComplexBehavior.__init__(self, doer, world, chanceOfAction)
        self.add(Carry(doer, world, chanceOfAction))
        self.add(Approach(doer, world, chanceOfAction, senseDistance, toGather))



class Mate(SenseFamilial):
    def __init__(self, doer, world, chanceOfAction = 0.05, potentialMates = ['Drone']):
        SenseFamilial.__init__(self, doer, world, chanceOfAction, None, False)
        self.potentialMates = potentialMates
        
    def senseAction(self, inRange):
        mate = inRange[0]
        if not self.potentialMates or mate.getSpecies() in self.potentialMates:
            babies = randint(1,5)
            birthingPlace = mate.getPosition()
            for i in xrange(babies):
                entities.Drone(self.world, self.doer.getFamily(), birthingPlace)
            self.doer.health = (float(self.doer.health) / 10.0) - 10
            self.doer.removeBehavior(Approach)
#            self.doer.getFamily().allyWith(mate.getFamily())
            print '%s gave birth %s Drones' % (self.doer, babies)

class Multiply(Behavior):
    def __init__(self, doer, world, chanceOfAction = 1.00, maxOffspring = 1, maxDistance = 1):
        Behavior.__init__(self, doer, world, chanceOfAction)
        self.maxOffspring = maxOffspring
        self.maxDistance = maxDistance

    def do(self):
        if self.shouldExecuteBehavior():
            doerClass = self.doer.__class__
            doerFamily = self.doer.getFamily()
            doerClass(self.world, doerFamily, randomizePosition(self.doer.getPosition(), self.maxDistance))
            for i in xrange(self.maxOffspring - 1):
                if self.shouldExecuteBehavior():
                    doerClass(self.world, doerFamily, randomizePosition(self.doer.getPosition(), self.maxDistance))
    
            
class Mutate(Behavior):
    def __init__(self, doer, world, chanceOfAction = 1.00, mutationProbabilities = {}):
        Behavior.__init__(self, doer, world, chanceOfAction)
        self.mutationProbabilities = mutationProbabilities

    def getChanceOfAction(self):
        possibleMutations = self.mutationProbabilities.keys()
    
        chance = 0.0
        for p in self.mutationProbabilities.itervalues():
            chance += p
    
        if entities.Queen in possibleMutations and self.doer.getFamily().getMemberCount(entities.Queen) == 0:
            chance *= 2

        return chance
        
    def do(self):
        if self.shouldExecuteBehavior():
            newEntity = choice(self.mutationProbabilities.keys())
            e = newEntity(self.world, self.doer.getFamily(), self.doer.getPosition())
            self.world.unregister(self.doer)
            print 'Mutated into', e.getSpecies()
    
class Decay(Behavior):
    def __init__(self, doer, world, chanceOfAction = 1.00, halfLife = 20):
        Behavior.__init__(self, doer, world, chanceOfAction)
        self.decayRate = log(2) / float(halfLife * 500) 
        
    def decay(self):
        self.doer.health = self.doer.health * exp(-1 * self.decayRate * self.doer.getAge())

    def getChanceOfDeath(self):
        health = self.doer.getHealth()
        if health <= 0:
            return 1
        else:
            return atan(float(self.doer.getAge())/float(health * 100)) - math.pi/2.0 + 1.0

    def die(self):
        print '%s died of old age' % self.doer.getSpecies()
        self.world.unregister(self.doer)
        
    def do(self):
        self.decay()
        if self.getChanceOfDeath() > random():
            self.die()
        
class Explode(Decay):
    def __init__(self, doer, world, chanceOfAction = 1.00, halfLife = 20):
        Decay.__init__(self, doer, world, chanceOfAction, halfLife)
        
    def die(self):
        origin = self.doer.getPosition()
        dimensions = self.doer.getDimensions()
        area = dimensions[0] * dimensions[1]
        offspringCount = int(round(float(area) / 128.0))

        if offspringCount > 1:
            for i in xrange(offspringCount):
                entities.Drone(self.world, self.doer.getFamily(), origin)
        
        Decay.die(self)
        
    
class Pop(Sense):
    def __init__(self, doer, world, chanceOfAction = 1.00):
        Sense.__init__(self, doer, world, chanceOfAction, 10)
    
    def senseAction(self, inRange):
        def entityExplodes(e): return e.hasBehavior(Explode)
        
        explodables = filter(entityExplodes, inRange)

        if explodables:
            toPop = explodables[0]
            print 'Popped', toPop
            Explode(toPop, self.world, 1).die()
            

class StartNewFamily(SenseFamilial):
    def __init__(self, doer, world, chanceOfAction = 0.00, senseDistance = None, senseFamily = True):
        SenseFamilial.__init__(self, doer, world, 1.00 - chanceOfAction, senseDistance, senseFamily)
    
    def doToWithinRange(self, func = None):
        if not SenseFamilial.doToWithinRange(self, func):
            fam = self.doer.getFamily()
            famBox = fam.getBoundingBox()
            if self.doer.age > 50 and fam.getMemberCount() > 5 and getMagnitude(getDisplacement(self.doer.getBoundingBox(), famBox)) >= fam.getTerritoryRadius() - 5:
                self.world.removeFromFamily(fam, self.doer)
                self.doer.family = entities.Family(self.world)
                print '%s started a new Family' % self.doer
                return True
        return False

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
