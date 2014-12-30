python-computational-geometry
=============================

Python library for vectorized geometry maths. 

Intended features:

    Fast, vecorized computations on sets of geometry objects

    Functions implemented in numpy and possibly cgal or other C libs

    Object oriented geometries with complimentary methods 
      (Segment.intersects_bezier and Bezier.intersects_segment 
      both use the same function under the hood, though order of
      results depends on which way it's called)

    Just-in-time computation and caching of properties (like 
      line normals, matrix determinants, etc.) to minimize 
      redundant calculations.
