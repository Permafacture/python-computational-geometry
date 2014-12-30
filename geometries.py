'''
Definitions of Geometry objects
'''
import geometric_tests
from types import MethodType
import numpy as np

def test_key(key):
    '''function for filtering geometric_tests.__dict__ keys
    based on whats a geometric test and what isn't'''
    key = key.split('_')
    if len(key) >= 2:
      #possibly
      if key[0]:
        return True
    return False

g_tests = {key:val for key,val in geometric_tests.__dict__.items() if test_key(key)}
#del g_tests['raw_input']

def key2method(name):
    '''Create methods for geometry `name` based on the functions in 
    geometric tests.  Do this by creating a dictionary of geometric 
    tests, renaming the key to suit the geometry object it will be a 
    method for.  So, take the function at geom_name_intersects_aabb 
    and make it the method `intersects_aabb(self, aabb1)` for a 
    geometry object with name=geom.  In the case that the test was
    defined with the arguments switched around (aabb1.intersects(geom))
    ask the test to reverse the order of its arguments.

    result should be used to update the object's __dict__
    '''
    result = {}
    for key,func in g_tests.items():
      parts = key.split('_')
      if parts[0] == name:
        result['_'.join(parts[1:])] = func
      elif parts[-1] == name and len(parts) == 3:
        result['_'.join(reversed(parts[:-1]))] = func
    return result

def geometry(cls):
    '''wrapper for geometry objects to populate
    them with relevant attributes from geometric_tests'''
    def give_attributes(*args,**kwargs):
        #http://stackoverflow.com/questions/10233553/bind-a-method-that-calls-other-methods-inside-the-class
        for key,func in key2method(cls.name).items():
          #setattr(Segments2d,key,MethodType(func,Segments2d))
          setattr(cls,key,func)
        return cls(*args,**kwargs)
    give_attributes.__name__ = cls.__name__
    give_attributes.__doc__ = cls.__doc__
    
    return give_attributes    

class Geometry(object):
    '''Meta class for all geometry objects'''
    def __init__(self,shape=None,dtype=np.float64):
        '''shape is the shape of an array of one geometry of
        this type.'''
        self._data   = None #user accessible
        self.to_add = []
        self.shape=shape
        self.dtype=dtype
        self.properties = []

    def add_data(self,geoms):
        '''add geometries to this object, either as list or 
        numpy array. either one at a time or a list/array
        of many.  self.data is set to None, and will be 
        re-compiled when next accessed'''
        geoms = np.array(geoms,dtype=self.dtype)
        if geoms.shape == self.shape:
          #this is just one geometry
          geoms=np.array([geoms])
        elif geoms.shape[1:] == self.shape:
          pass
        else:
          raise ValueError("Expected shape: Nx%s | got: %s"%(self.shape,geoms.shape))
        self.to_add.append(geoms)

    def clear_properties(self):
        '''sets all computed properties to None, for when the
        properties are dirty and need to be recalculated if used'''
        for p in self.properties:
          setattr(self,'_%s'%p,None)
   
    def compile(self):
        '''Append recently added data to older data.
        after this, self.data will have all geometries
        and can be accessed without further computations''' 

        if self._data:
          geoms = [self._data]+to_add
        else:
          geoms = self.to_add
        self._data = np.concatenate(geoms)
        self.to_add = []
        self.clear_properties()

    @property
    def data(self):
      if self.to_add:
        self.compile()
      return self._data
       

@geometry
class Segments2d(Geometry):
    '''An array of 2D line segments defined by
    [x_begin,y_begin,x_end,y_end]'''
    name = 'segments2d'

    def __init__(self):
        Geometry.__init__(self,shape=(4,))

        #boiler plate: append to properties, clear_properties
        #define @property decorated property.  write a 
        #create_property(self)
        self.properties.append('normals')
        self.clear_properties()

    @property
    def normals(self):
      if not self._normals:
        self.create_normals()
      return self._normals

    def create_normals(self):
        '''segs = [[x1,y1,x2,y2],...] => normals [[xn,yn],...]'''
        segs = self.data
        result = segs[:,2:] - segs[:,:2]
        tmp = np.empty((len(segs),3),dtype=segs.dtype)
        tmp[:,:2] = np.square(result)
        tmp[:,2] = np.add(tmp[:,0],tmp[:,1])
        tmp[:,2] = np.sqrt(tmp[:,2])
        #lame, why do this in two step?
        result[:,0] = result[:,0] / tmp[:,2]
        result[:,1] = result[:,1] / tmp[:,2]
        self._normals = result
      

if __name__ == '__main__':
  n = 10
  t = np.linspace(0,2*np.pi,n)

  segs1 = Segments2d()
  rays1 = np.zeros((n,4),dtype=np.float32)
  rays1[:,2] = np.cos(t)
  rays1[:,3] = np.sin(t)
  segs1.add_data(rays1)

  segs2 = Segments2d()
  rays2 =np.ones((n,4),dtype=np.float32)
  rays2[:,2] = 1+np.cos(t)
  rays2[:,3] = np.sin(t)
  segs2.add_data(rays2)

  pts1,mask1 = segs1.intersection_segments2d(segs2)
  pts2,mask2 = segs2.intersection_segments2d(segs1)


