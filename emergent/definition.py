from random import randint

from behaviors import RandomMove, ApproachFamily, Mutate, Decay, StartNewFamily, Eat, Gather, Mate, Absorb, Explode, Multiply
from entities import Personality, Genotype

def apply():
    from entities import Drone, Queen, Hunter, Food

    Drone.entityBehaviors = Personality([
                                RandomMove(
                                    chanceOfAction=1.0
                                ),
                                
                                ApproachFamily(
                                    chanceOfAction=0.75,
                                    senseDistance=100,
                                    senseFamily=False,
                                    toApproach=[Queen]
                                ),
                                
                                Mutate(
                                    chanceOfAction=1.0,
                                    mutationProbabilities={Hunter: 0.0005, 
                                                           Queen: 0.0025}
                                ),
                                
                                Decay(
                                    chanceOfAction=1.0,
                                    halfLife=80
                                ),
                                
                                StartNewFamily(
                                    chanceOfAction=0.01
                                ),
                                
                                Eat(
                                    chanceOfAction=0.50
                                ),
                                
                                Gather(
                                    chanceOfAction=0.50,
                                    senseDistance=100,
                                    toGather=[Food]
                                )
                            ])
        
    
    
    Drone.attributes = Genotype(
                            health=lambda:randint(200,400),
                            dimensions=(5, 5),
                            color=(0, 0, 200),
                            growthFactor=0.25
                        )
    
    Queen.entityBehaviors = Personality([
                                RandomMove(
                                  chanceOfAction=1.0
                                ),
                                
                                ApproachFamily(
                                  chanceOfAction=0.75,
                                  senseDistance=200,
                                  senseFamily=False,
                                  toApproach=[Drone],
                                ),
                                
                                Mate(
                                  chanceOfAction=0.10
                                ),
                                
                                Decay(
                                  chanceOfAction=1.0,
                                  halfLife=125,
                                ),
                                
                                Absorb(
                                  chanceOfAction=1.0,
                                  toAbsorb=[Queen],
                                ),
                                
                                StartNewFamily(
                                  chanceOfAction=0.01
                                )
                            ])
    
    Queen.attributes = Genotype(
                            health=lambda:randint(500,1000),
                            dimensions=lambda:[randint(6,10)]*2,
                            color=(0, 200, 0),
                            growthFactor=0.25
                        )
    
    Hunter.entityBehaviors = Personality([
                                Absorb(
                                  chanceOfAction=0.025
                                ),
                                
                                ApproachFamily(
                                  chanceOfAction=0.75,
                                  senseDistance=50,
                                  senseFamily=False
                                ),
                            
                                Mutate(
                                  chanceOfAction=1.0,
                                  mutationProbabilities={Queen: 0.0005}
                                ),
                                
                                Explode(
                                  chanceOfAction=1.0,
                                  halfLife=2
                                ),
                                
                                StartNewFamily(
                                  chanceOfAction=0.01
                                )
                            ])
    
    Hunter.attributes = Genotype(
                            health=lambda:randint(200,300),
                            dimensions=(3,3),
                            color=(200, 0, 0),
                            growthFactor=0.175
                        )
    
    Food.entityBehaviors = Personality([
                                Multiply(
                                  chanceOfAction=0.001,
                                  maxOffspring=10,
                                  maxDistance=25
                                ),
                                
                                Decay(
                                  chanceOfAction=1,
                                  halfLife=500
                                )
                            ])
                            
    Food.attributes = Genotype(
                            health=lambda:randint(200,400),
                            dimensions=lambda:[randint(2,10)]*2,
                            color=(133, 88, 10),
                            growthFactor=0.25
                        )
