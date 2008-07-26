from random import randint, random, choice
import math
from math import exp, log, atan

from pygame import Rect

from common import *
import entities



class Behavior(object):
    def __init__(self, chanceOfAction=1.00):
        self.chanceOfAction = chanceOfAction

    def getChanceOfAction(self):
        return self.chanceOfAction

    def setChanceOfAction(self, chance):
        self.chanceOfAction = chance
        return self

    def shouldExecuteBehavior(self):
        return self.getChanceOfAction() > random()

    def do(self, doer, world):
        raise NotImplementedError()
    
    def __eq__(self, other):
        return self.__class__ is other.__class__

    def __ne__(self, other):
        return not self.__eq__(other)

class ComplexBehavior(Behavior):
    def __init__(self, chanceOfAction=1.00):
        Behavior.__init__(self, chanceOfAction)
        self.behaviors = []
        
    def add(self, toAdd):
        self.remove(toAdd)
        self.behaviors.append(toAdd)
        
    def remove(self, toRemove):
        try:
            self.behaviors.remove(toRemove)
        except ValueError:
            pass

    def __iter__(self):
        for b in self.behaviors:
            yield b
    
    def do(self, doer, world):
        for b in self.behaviors:
            b.do(doer, world)
    

class Move(Behavior):
    def __init__(self, chanceOfAction=1.00, displacement=(0, 0)):
        Behavior.__init__(self, chanceOfAction)
        self.displacement = displacement
        
    def do(self, doer, world):
        box = doer.boundingBox
        newBox = box.move(*self.displacement)
        doer.boundingBox = Rect(newBox.left%RESOLUTION[0], newBox.top%RESOLUTION[1], newBox.w, newBox.h)

        carriedEntity = doer.carriedEntity
        if carriedEntity:
            carriedEntityBox = carriedEntity.boundingBox
            newCarriedEntityBox = carriedEntityBox.move(self.displacement[0], self.displacement[1])
            doer.carriedEntity.boundingBox = Rect(newCarriedEntityBox.left%RESOLUTION[0], newCarriedEntityBox.top%RESOLUTION[1], newCarriedEntityBox.w, newCarriedEntityBox.h)
        
        
        
class RandomMove(Move):
    def __init__(self, chanceOfAction = 1.00):
        Move.__init__(self, chanceOfAction)

    def do(self, doer, world):
        stride = round(doer.getDimensions()[0] / 2)
    
        dx = randint(-1 * stride, stride)
        dy = randint(-1 * stride, stride)
        self.displacement = (dx, dy)
        return Move.do(self, doer, world)

class Sense(Behavior):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None):
        Behavior.__init__(self, chanceOfAction)
        if senseDistance:
            self.senseDistance = senseDistance
        else:
            self.senseDistance = 1

    def updateSenseDistance(self, doer, world):
        self.senseDistance = doer.getDimensions()[0] + 1
    
    def senseAction(self, doer, world, inRange):
        pass

    def othersInRange(self, doer, world):
        self.updateSenseDistance(doer, world)
        senseBox = doer.boundingBox.inflate(self.senseDistance, self.senseDistance)
        return world.checkNeighbors(doer, senseBox)

    def filterTargets(self, possibleTargets, targetEntities):
        if possibleTargets and targetEntities:    
            def filterEntities(e):
                return e.__class__ in targetEntities
            possibleTargets = filter(filterEntities, possibleTargets)
        return possibleTargets
        

    def doToWithinRange(self, doer, world, func=None):
        if func is None:
            func = self.senseAction
            
        inRange = self.othersInRange(doer, world)
        if inRange and self.shouldExecuteBehavior():
            func(doer, world, inRange)
            return True
        else:
            return False

    def do(self, doer, world):
        self.doToWithinRange(doer, world)

class SenseFamilial(Sense):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None, senseFamily = True):
        Sense.__init__(self, chanceOfAction, senseDistance)
        self.senseFamily = senseFamily

    def othersInRange(self, doer, world):
        def familial(e):
            if self.senseFamily:
                return e.getFamily() == doer.getFamily()
            else:
                return e.getFamily() != doer.getFamily()

        inRange = Sense.othersInRange(self, doer, world)
        return filter(familial, inRange)

        
class Response(Move, Sense):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None):
        Move.__init__(self, chanceOfAction)
        Sense.__init__(self, chanceOfAction, senseDistance)

class Approach(Response):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None, toApproach = []):
        Response.__init__(self, chanceOfAction, senseDistance)
        self.randomMove = RandomMove()
        self.toApproach = toApproach

    def othersInRange(self, doer, world):
        return self.filterTargets(Response.othersInRange(self, doer, world), self.toApproach)        

    def senseAction(self, doer, world, inSight):
        toApproach = inSight[0]
#            print 'Found %s' % toApproach
        self.displacement = normalize(getDisplacement(doer.boundingBox, toApproach.boundingBox))

        if self.displacement[0] == 0 and self.displacement[1] == 0:
            self.randomMove.do(doer, world)
        else:
            self.displacement[0] = round(self.displacement[0] * 2)
            self.displacement[1] = round(self.displacement[1] * 2)

            Move.do(self, doer, world)

    def do(self, doer, world):
        if self.doToWithinRange(doer, world) == False:
            self.randomMove.do(doer, world)

class ApproachFamily(Approach, SenseFamilial):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None, senseFamily = True, toApproach = []):
        SenseFamilial.__init__(self, chanceOfAction, senseDistance, senseFamily)
        Approach.__init__(self, chanceOfAction, senseDistance, toApproach)

    def othersInRange(self, doer, world):
        return self.filterTargets(SenseFamilial.othersInRange(self, doer, world), self.toApproach)        
        

class Avoid(Response):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None, toAvoid = []):
        Response.__init__(self, chanceOfAction, senseDistance)
        self.toAvoid = toAvoid
        
    def senseAction(self, doer, world, inSight):
        # take the average vector of all the things to avoid within sight range 
        pass

class Absorb(SenseFamilial):
    def __init__(self, chanceOfAction = 1.00, toAbsorb = []):
        SenseFamilial.__init__(self, chanceOfAction, None, False)
        self.toAbsorb = toAbsorb
        self.chanceOfAction = .1
        
    def updateSenseDistance(self, doer, world):
        self.senseDistance = doer.getDimensions()[0] + 1

    def othersInRange(self, doer, world):
        return self.filterTargets(SenseFamilial.othersInRange(self, doer, world), self.toAbsorb)        

    def senseAction(self, doer, world, inRange):
        for e in inRange:
            doer.grow(e.getDimensions())
            world.unregister(e)
            
class Eat(Sense):
    def othersInRange(self, doer, world):
        return self.filterTargets(Sense.othersInRange(self, doer, world), [entities.Food])

    def senseAction(self, doer, world, edibles):
        toEat = edibles[0]
        toEat.feed(doer)
#        print '%s is eating %s' % (doer, toEat)
        
class Carry(Sense):
    def othersInRange(self, doer, world):
        return self.filterTargets(Sense.othersInRange(self, doer, world), [entities.Food])

    def senseAction(self, doer, world, inRange):
        if doer.isCarryingEntity():
#            print 'Dropping', doer.carriedEntity
            doer.dropEntity()
        else:
            for e in inRange:
                if not e.beingCarried:
                    doer.carryEntity(e)
                    break

#            print 'Picking up', doer.carriedEntity

class Gather(ComplexBehavior):
    def __init__(self, chanceOfAction = 1.00, senseDistance = None, toGather = []):
        ComplexBehavior.__init__(self, chanceOfAction)
        self.add(Carry(chanceOfAction))
        self.add(Approach(chanceOfAction, senseDistance, toGather))



class Mate(SenseFamilial):
    def __init__(self, chanceOfAction = 0.05, potentialMates = ['Drone']):
        SenseFamilial.__init__(self, chanceOfAction, None, False)
        self.potentialMates = potentialMates
        
    def senseAction(self, doer, world, inRange):
        mate = inRange[0]
        if not self.potentialMates or mate.getSpecies() in self.potentialMates:
            babies = randint(1,5)
            birthingPlace = mate.getPosition()
            for i in xrange(babies):
                entities.Drone(world, doer.getFamily(), birthingPlace)
            doer.health = (float(doer.health) / 10.0) - 10
            doer.removeBehavior(Approach)
#            doer.getFamily().allyWith(mate.getFamily())
            print '%s gave birth %s Drones' % (doer, babies)

class Multiply(Behavior):
    def __init__(self, chanceOfAction = 1.00, maxOffspring = 1, maxDistance = 1):
        Behavior.__init__(self, chanceOfAction)
        self.maxOffspring = maxOffspring
        self.maxDistance = maxDistance

    def do(self, doer, world):
        if self.shouldExecuteBehavior():
            doerClass = doer.__class__
            doerFamily = doer.getFamily()
            doerClass(world, doerFamily, randomizePosition(doer.getPosition(), self.maxDistance))
            for i in xrange(self.maxOffspring - 1):
                if self.shouldExecuteBehavior():
                    doerClass(world, doerFamily, randomizePosition(doer.getPosition(), self.maxDistance))
    
            
class Mutate(Behavior):
    def __init__(self, chanceOfAction = 1.00, mutationProbabilities = {}):
        Behavior.__init__(self, chanceOfAction)
        self.mutationProbabilities = mutationProbabilities

    def getChanceOfAction(self):
        possibleMutations = self.mutationProbabilities.keys()
    
        chance = 0.0
        for p in self.mutationProbabilities.itervalues():
            chance += p
    
#        if entities.Queen in possibleMutations and self.doer.getFamily().getMemberCount(entities.Queen) == 0: # PROBLEM
#            chance *= 2

        return chance
        
    def do(self, doer, world):
        if self.shouldExecuteBehavior():
            newEntity = choice(self.mutationProbabilities.keys())
            e = newEntity(world, doer.getFamily(), doer.getPosition())
            world.unregister(doer)
            print 'Mutated into', e.getSpecies()
    
class Decay(Behavior):
    def __init__(self, chanceOfAction = 1.00, halfLife = 20):
        Behavior.__init__(self, chanceOfAction)
        self.decayRate = log(2) / float(halfLife * 500) 
        
    def decay(self, doer, world):
        doer.health = doer.health * exp(-1 * self.decayRate * doer.age)

    def getChanceOfDeath(self, doer, world):
        health = doer.health
        if health <= 0:
            return 1
        else:
            return atan(float(doer.age)/float(health * 100)) - math.pi/2.0 + 1.0

    def die(self, doer, world):
        print '%s died of old age' % doer.getSpecies()
        world.unregister(doer)
        
    def do(self, doer, world):
        self.decay(doer, world)
        if self.getChanceOfDeath(doer, world) > random():
            self.die(doer, world)
        
class Explode(Decay):
    def __init__(self, chanceOfAction = 1.00, halfLife = 20):
        Decay.__init__(self, chanceOfAction, halfLife)
        
    def die(self, doer, world):
        origin = doer.getPosition()
        dimensions = doer.getDimensions()
        area = dimensions[0] * dimensions[1]
        offspringCount = int(round(float(area) / 128.0))

        if offspringCount > 1:
            for i in xrange(offspringCount):
                entities.Drone(world, doer.getFamily(), origin)
        
        Decay.die(self, doer, world)
        
    
class Pop(Sense):
    def __init__(self, chanceOfAction = 1.00):
        Sense.__init__(self, chanceOfAction, 10)
    
    def senseAction(self, doer, world, inRange):
        explodables = [entity for entity in inRange 
                        if entity.hasBehavior(Explode)]

        if explodables:
            toPop = explodables[0]
            print 'Popped', toPop
            Explode(toPop, world, 1).die()
            

class StartNewFamily(SenseFamilial):
    def __init__(self, chanceOfAction = 0.00, senseDistance = None, senseFamily = True):
        SenseFamilial.__init__(self, 1.00 - chanceOfAction, senseDistance, senseFamily)
    
    def doToWithinRange(self, doer, world, func = None):
        if not SenseFamilial.doToWithinRange(self, doer, world, func):
            fam = doer.getFamily()
            famBox = fam.boundingBox
            if doer.age > 50 and fam.getMemberCount() > 5 and getMagnitude(getDisplacement(doer.boundingBox, famBox)) >= fam.getTerritoryRadius() - 5:
                world.removeFromFamily(fam, doer)
                doer.family = entities.Family(world)
                print '%s started a new Family' % doer
                return True
        return False

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
