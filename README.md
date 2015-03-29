python-computational-geometry
=============================

Python library for vectorized geometry maths. 

Intended features:

    Fast, vecorized computations on sets of geometry objects

    Functions implemented in numpy and possibly cgal or other C libs

    Object oriented geometries with complimentary methods 
      (Intersect(bezier1,linesegs1) Intersect(linesegs1,bezier1)
      both use the same function under the hood.

    Just-in-time computation and caching of properties (like 
      line normals, matrix determinants, etc.) to minimize 
      redundant or uneeded calculations.
