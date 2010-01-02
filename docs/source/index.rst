========
Emergent
========

.. toctree::
   :maxdepth: 2

Emergent is my humble attempt at creating emergent behavior

Quick Links
===========

* `code repository <http://github.com/clofresh/emergent>`_
* `API documentation <api/index.html>`_

Requirements
============

`pygame <http://www.pygame.org/>`_ (tested with 1.8.1)

Installation
============

``sudo python setup.py install``

Usage
=====

``/usr/local/bin/emergent``


What's going on
===============

Entities
--------

Entity is the general name of the different squares in the world. Each entity has a distinct personality comprised of various complex behaviors. Each entity also belongs to a family and will interact differently with entities of the same or different Families.

Drones
^^^^^^

The blue entities are Drones. They have a random chance of mutating into Queens or Hunters. They will approach queens of different families and try to mate with them. They will also eat and push Food around. Eating Food lets drones grow larger and have longer strides when they move.

Queens
^^^^^^

The green entities are Queens. They will approach Drones of different families and try to mate with them. Each offspring the the Queen produces takes a toll on her health.

Hunters
^^^^^^^

The red entities are Hunters. They will approach entities from other families and absorb them, allowing them to grow larger. Hunters have a random chance of exploding, producing a number of offspring proportional to their size.

Food
^^^^

The brown entities are Food. They can't move on their own, but Drones can push them around. Over time, Food entities will generate other Food entities nearby.




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

