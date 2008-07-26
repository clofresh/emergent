import emergent
from mocker import Mocker, expect
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
    

tests = [testBehavior, testComplexBehavior, testMove, testRandomMove]
    

if __name__ == '__main__':
    for test in tests:
        test()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
