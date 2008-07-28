import emergent
from mocker import Mocker, expect, ANY
from pygame import Rect



def testBehavior():
    from emergent.behaviors import Behavior
    from emergent.entities import Entity
    from emergent.playing import World
    
    b = Behavior()
    assert b == Behavior()
    assert b != object()
    
    m = Mocker()
    world = m.mock(World)
    doer = m.mock(Entity)
    
    try:
        b.do(doer, world)
        assert False, 'Behavior.do should raise NotImplementedError'
    except NotImplementedError:
        pass


def testComplexBehavior():
    from emergent.behaviors import Behavior, ComplexBehavior
    from emergent.entities import Entity
    from emergent.playing import World
    
    m = Mocker()
    world = m.mock(World)
    doer = m.mock(Entity)
    mockBehavior = m.mock(Behavior)

    complexBehavior = ComplexBehavior()
    
    complexBehavior.add(mockBehavior)
    assert mockBehavior in complexBehavior, 'Add failed: behaviors = %s' % complexBehavior.behaviors

    complexBehavior.remove(mockBehavior)
    assert mockBehavior not in complexBehavior, 'Remove failed: behaviors = %s' % complexBehavior.behaviors
    
    
    complexBehavior.add(mockBehavior)
    mockBehavior.do(doer, world)
    
    m.replay()
    complexBehavior.do(doer, world)        
    m.verify()
        
def testMove():
    from emergent.behaviors import Move
    from emergent.entities import Entity
    from emergent.playing import World
    
    m = Mocker()
    world = m.mock(World)
    
    start = (0, 0)
    movement = (10, 20)
    
    doer = Entity(world, position=start)
    move = Move(displacement=movement)

    assert doer.boundingBox.topleft == start
    move.do(doer, world)
    assert doer.boundingBox.topleft == tuple(start + offset
                                            for start, offset 
                                            in zip(start, movement)), 'Move failed. Start: %s, End: %s' % (start, doer.boundingBox.topleft)
    

def testRandomMove():
    from emergent.behaviors import Move, RandomMove
    from emergent.entities import Entity, Genotype
    from emergent.playing import World
    
    m = Mocker()
    world = m.mock(World)
    
    start = (0, 0)
    movements = [start]
    
    class TestEntity(Entity): 
        # Make sure that entity dimensions are sufficiently large enough to move
        attributes = Genotype(dimensions=(10,10))

    # Assumes Move works correctly
    mover = TestEntity(world, position=start)
    randomMover = TestEntity(world, position=start)

    print 'Resolution: %s' % str(emergent.common.RESOLUTION)
    print 'Start: %s' % str(start)
    assert mover.boundingBox.topleft == start    
    assert randomMover.boundingBox.topleft == start    

    for i in xrange(10):
        randomMove = RandomMove()
        randomMove.do(randomMover, world)

        move = Move(displacement=randomMove.displacement)

        print 'Displacement: %s' % str(randomMove.displacement)

        move.do(mover, world)
        print 'RandomMover: %s, Mover: %s' % (randomMover.boundingBox, mover.boundingBox)

        assert randomMover.boundingBox == mover.boundingBox
    
def testSense():
    from emergent.behaviors import Sense
    from emergent.entities import Entity, Genotype
    from emergent.playing import World

    entitySize = 10
    class TestEntity(Entity): 
        attributes = Genotype(dimensions=tuple([entitySize] * 2))

    class SenseActionException(Exception):
        ''' Make a fake exception so that we can catch it
            to verify that the senseAction gets called
        '''
        
    def dummySenseAction(doer, world, inRange):
        raise SenseActionException()

    startingPositions = [(0,0), 
                         (entitySize * 2,0), 
                         (0, entitySize * 2), 
                         (entitySize * 3, 0)]
    world = World()
    sense = Sense(senseDistance=entitySize + 1)
    sense.senseAction = dummySenseAction

    entities = [TestEntity(world, position=startingPosition)
                for startingPosition in startingPositions]

    expectedInRange = entities[1:3]
    actualInRange = sense.othersInRange(entities[0], world)

    assert actualInRange == expectedInRange, 'expected inRange: %s, actual: %s' % (expectedInRange, actualInRange)
    
    
    try:
        sense.do(entities[0], world)
        assert False, "Didn't call sense action"
    except SenseActionException:
        pass # Correct behavior
    
    sense = Sense(senseDistance=0)
    try:
        sense.do(entities[0], world)
    except SenseActionException:
        assert False, "Called sense action when no targets in range"



def testSenseFamilial():
    from emergent.behaviors import SenseFamilial
    from emergent.entities import Entity, Family, Genotype
    from emergent.playing import World

    entitySize = 10
    class TestEntity(Entity): 
        attributes = Genotype(dimensions=tuple([entitySize] * 2))

    class SenseActionException(Exception):
        ''' Make a fake exception so that we can catch it
            to verify that the senseAction gets called
        '''
        
    def dummySenseAction(doer, world, inRange):
        raise SenseActionException()

    world = World()

    familyCount = 2
    startingPositions = [(0,0), 
                         (entitySize * 2,0)]

    families = [Family(world, 'Family %s' % i) 
                for i in xrange(familyCount)]
    entities = [TestEntity(world, family, startingPosition) 
                for family, startingPosition 
                in zip(families, startingPositions)]

    senseDistance = entitySize + 1
    senseFamilial = SenseFamilial(senseDistance=senseDistance,
                                  senseFamily=True)
    senseFamilial.senseAction = dummySenseAction
    
    assert senseFamilial.othersInRange(entities[0], world) == []
    
    senseNonfamilial = SenseFamilial(senseDistance=senseDistance,
                                     senseFamily=False)
    senseNonfamilial.senseAction = dummySenseAction
    
    assert senseNonfamilial.othersInRange(entities[0], world) == entities[1:2]
    
    
    
        
    

tests = [testBehavior, testComplexBehavior, testMove, testRandomMove, testSense, testSenseFamilial]
    

if __name__ == '__main__':
    for test in tests:
        test()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
