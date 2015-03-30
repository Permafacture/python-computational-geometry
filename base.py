'''
Not used right now.  At somepoint, having a base class
that keeps track of named axis and cached properties 
would be useful...

I want BaseGeometries, ComplexGeometries and Results
to all get thier axes from the thing that comtains them,
like when a Line2d contains two Vec2ds, and a result
contains multiple Vec1ds, Vec2ds and/or Vec3ds.

'''

class CachedDictionary(object):
    '''provides a dictionary interface to an object that caches
    results.  Keys that would still require calcuation are
    available through uncached_keys(). (Immediately available
    data can be found in the self._cached dict)'''

    def __init__(self):
        '''Does not take any arguments on initialization'''
        self._notyetcached = []
        self._cached = {}
        for k,i in self.locals
        pass

    def keys(self):
        return self._data.keys()+self._notyetcached.keys()

    def __setitem__(self,key,value):
        '''Forbids setting a key that is cachable'''
        if key not in self._notyetcached.keys():
          self._data[key] = value
        else:
          raise ValueError(
                "%s is cachable and cannot be set manually"%(key))
    def 
