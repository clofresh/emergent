from random import randint

import pygame
from pygame import event
from pygame.event import Event

from states import GuiState
from gui import Paintable, Updateable
from common import randomizePosition
from entities import Drone, Queen, Hunter, Family, Food
import definition

class PlayingGameState(GuiState):
 
    def __init__(self):
        GuiState.__init__(self)

        gameWorld = World()
        definition.apply()

        variance = 50

        for i in xrange(5):
            q = Drone(gameWorld)
            fam = q.getFamily()
            home = q.getPosition()
            f = Food(gameWorld, None, randomizePosition(home, 100))
            foodFam = f.getFamily()
            for j in xrange(10):
                Drone(gameWorld, fam, randomizePosition(home, 50))
                
            for j in xrange(15):
                Food(gameWorld, foodFam, randomizePosition(home, 100))
                      
      

#        for i in xrange(20):
#            Drone(gameWorld)
#            Food(gameWorld)      
            
#        foodFam = f.getFamily()
#        for i in xrange(10):
#            Food(gameWorld, foodFam)


        self.add(gameWorld)


        


class World(Paintable, Updateable):
    def __init__(self):
        Paintable.__init__(self)
        self.entities = []
        self.families = {}

    def __del__(self):
        del self.entities
        del self.families
        
    def paint(self, screen):
        for e in self.entities:
            e.paint(screen)
            
        for f in self.families.iterkeys():
            f.paint(screen)
        
    def update(self, delay):
        for e in self.entities:
            self.addToFamily(e.getFamily(), e)
            e.update(delay, self)
            
        emptyFamilies = []
        for family in self.families.iterkeys():
            family.update(delay, self)
            if family.getMemberCount() == 0:
                emptyFamilies.append(family)
                
        for emptyFamily in emptyFamilies:
            del self.families[emptyFamily]
        del emptyFamilies
                
        if not self.entities:
            print "Everyone's dead!"
            event.post(Event(pygame.QUIT, {}))
            
    def addToFamily(self, family, member):
        try:
            if not member in self.families[family]:
                self.families[family].append(member)
        except KeyError:
            self.families[family] = [member]

    def removeFromFamily(self, family, member):
        try:
            self.families[family].remove(member)
        except:
            pass
    
    def getFamilyMembers(self, family):
        return self.families[family]
    
    def register(self, entity):
#        print 'Registering ', entity
        self.entities.append(entity)
        
    def unregister(self, entity):
#        print 'Unregistering ', entity
        try:
            if entity.__class__ != Family:
                try:
                    self.families[entity.getFamily()].remove(entity)
                except KeyError:
                    pass
            self.entities.remove(entity)
#            e = self.entities.pop(self.entities.index(entity))
#            del e
#            del entity
        except ValueError:
            pass
                
    def checkNeighbors(self, entity, senseBox):
        neighbors = []  
        for e in self.entities:
            if e.__class__ is not Family and e is not entity and senseBox.colliderect(e.boundingBox):
                neighbors.append(e)

        return neighbors
    



        