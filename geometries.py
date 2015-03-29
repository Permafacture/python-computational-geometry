'''
Definitions of Geometry objects
'''
import geometric_tests
from types import MethodType
import numpy as np

## TODO make numpy array read only (geometry._data)
## TODO make segment, ray and line all the same
##       just let them apply their own parameter 
##       constraint in a method.

def test_key(key):
    '''function for filtering geometric_tests.__dict__ keys
    based on whats a geometric test and what isn't'''
    key = key.split('_')
    if len(key) == 3:
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



def key2method2(geomtype):
    '''Create methods for geometry type based on the functions 
    in geometric tests.  Do this by creating a dictionary of 
    geometric tests, renaming the key to suit the geometry object 
    it will be a  method for.  So, take the function at 
    geomtype_intersects_aabb and make it the method 
    `intersects_aabb(self, aabb1)` for a geometry object with 
    _type=geom.  In the case that the test was defined with 
    the arguments switched around (aabb1.intersects(geom)),
    the function should check and switch its arguments/result

    result should be used to update the object's __dict__
    '''
    result = {}
    tmp = {} #{intersects: {bbox: segs_intersects_bbox} }
    for key,func in g_tests.items():
      g1,funcname,g2 =  key.split('_') #geometric tests must be named g1_test_g2()
      if g1 == geomtype:
        tmp.setdefault(funcname,dict())[g2] = func
      elif g2 == geomtype:
        tmp.setdefault(funcname,dict())[g1] = func

    def make_dispatcher(fdict):
      '''closure for setting up a dispatcher for this function'''
      def dispatcher(*args,**kwargs):
        '''takes a dictionary of {name: func} and calls the
        correct function for name.'''
        #print args
        self=args[0]
        other=args[1]
        try: return fdict[other._type](self,other)
        except KeyError:
          raise AttributeError("%s does not have function %s for type %s")
      return dispatcher

    for funcname, fdict in tmp.items():
      #create a dispatching function for each type function name
      dispatcher = make_dispatcher(fdict)
      dispatcher.__name__ = funcname
      dispatcher.__doc__ = '''Dispatched %s function for %s.\ndefined for:'''%(funcname, geomtype) 
      dispatcher.__doc__ += '\n    '.join(fdict.keys())
      dispatcher.__doc__ += '\n(Should probably have more documentation here, but what?)' 
      result[funcname] = dispatcher
    return result

def geometry(cls):
    '''wrapper for geometry objects to populate
    them with relevant attributes from geometric_tests'''
    def give_attributes(*args,**kwargs):
        #http://stackoverflow.com/questions/10233553/bind-a-method-that-calls-other-methods-inside-the-class
        for key,func in key2method2(cls._type).items():
          #setattr(Segments2d,key,MethodType(func,Segments2d))
          setattr(cls,key,MethodType(func,None,cls))
          #print "set attr"
        return cls(*args,**kwargs)
    give_attributes.__name__ = cls.__name__
    give_attributes.__doc__ = cls.__doc__
    
    return give_attributes    

class Geometry(object):
    '''Meta class for all geometry objects'''
    def __init__(self,_geoms,shape=None,dtype=None):
        '''geoms is a list or numpy array of the geometry data'''
        if type(_geoms) == np.ndarray :
          if type(_geoms[0]) == np.ndarray:
            geoms=_geoms
            if geoms.dtype != dtype:
              geoms=np.array(geoms,dtype=dtype)
          else:
            geoms = np.array([_geoms],dtype=dtype)


        else:
            geoms = np.array(_geoms,dtype=dtype)
            if geoms.dtype==object:
              e = "Geometry can't instantiate with a %s"%type(_geom)
              raise ValueError(e)
            elif type(geoms[0]) != np.ndarray:
              geoms = np.array([geoms],dtype=dtype)
        if geoms[0].shape == shape:
          self._data = geoms
          self._properties = []
        else:
          e = "expected geometry.shape == %s, got %s"%(shape,geoms.shape)
          raise ValueError(e)

    def _clear_cache(self):
        '''sets all computed properties to None, for when the
        properties are dirty and need to be recalculated if used'''
        for p in self._properties:
          setattr(self,'_%s'%p,None)   

@geometry
class Segments2d(Geometry):
    '''An array of 2D line segments defined by
    [x_begin,y_begin,x_end,y_end]'''
    _type = 'segments2d'

    def __init__(self,geoms,dtype=None):
        Geometry.__init__(self,geoms,shape=(4,),dtype=dtype)
        #rename _data to make sense for a line segment
        self._points = self._data 

        #boiler plate: append to properties, clear_properties
        #define @property decorated property.  write a 
        #create_property(self)
        self._properties.append('normals')
        self._clear_cache()

    @property
    def normals(self):
      if not self._normals:
        self.create_normals()
      return self._normals

    def create_normals(self):
        '''segs = [[x1,y1,x2,y2],...] => normals [[xn,yn],...]'''
        segs = self._points
        result = segs[:,2:] - segs[:,:2]
        tmp = np.empty((len(segs),3),dtype=segs.dtype)
        tmp[:,:2] = np.square(result)
        tmp[:,2] = np.add(tmp[:,0],tmp[:,1])
        tmp[:,2] = np.sqrt(tmp[:,2])
        #lame, why do this in two step?
        result[:,0] = result[:,0] / tmp[:,2]
        result[:,1] = result[:,1] / tmp[:,2]
        self._normals = result
      
@geometry
class Segments3d(Geometry):
    '''An array of 3D line segments defined by
    [x_begin,y_begin,z_begin,x_end,y_end,z_end]'''
    _type = 'segments3d'

    def __init__(self,geoms,dtype=None):
        Geometry.__init__(self,geoms,shape=(6,),dtype=dtype)
        #rename _data to make sense for a line segment
        self._points = self._data 

        #boiler plate: append to properties, clear_properties
        #define @property decorated property.  write a 
        #create_property(self)
        self._properties.append('normals')
        self._clear_cache()

    @property
    def normals(self):
      if not self._normals:
        self.create_normals()
      return self._normals

    def create_normals(self):
        '''segs = [[x1,y1,z1,x2,y2,z2],...] => normals [[xn,yn,zn],...]'''
        segs = self._points
        result = segs[:,3:] - segs[:,:3]
        tmp = np.empty((len(segs),4),dtype=segs.dtype)
        tmp[:,:3] = np.square(result)
        #noticed that if the result of sum goes to an element
        #of the same array, that element is not part of the sum.
        #tmp[:,3] here is still garbage, so we can write over it
        tmp[:,3] = np.sum(tmp,axis=1,out=tmp[:,3]) # SAFE? seems to be
        tmp[:,3] = np.sqrt(tmp[:,3])
        #lame, why do this in two step?
        result[:,0] = result[:,0] / tmp[:,3]  #TODO use newaxis 
        result[:,1] = result[:,1] / tmp[:,3]  # and do 3 in 1!
        result[:,2] = result[:,2] / tmp[:,3]
        self._normals = result

@geometry
class Triangles(Geometry):
    '''An array of 3D triangles defined by
    [[v0,v1,v2],...] where v0 = [x0,y0,z0]'''
    _type = 'triangles'

    def __init__(self,geoms,dtype=None):
        Geometry.__init__(self,geoms,shape=(3,3),dtype=dtype)
        #rename _data to make sense for a line segment
        self._points = self._data 

        #boiler plate: append to properties, clear_properties
        #define @property decorated property.  write a 
        #create_property(self)
        self._properties.extend(['normals','parameters'])
        self._clear_cache()


    @property
    def parameters(self):
      if not self._parameters:
        self.create_parameters()
      return self._parameters

    def create_parameters(self):
        '''Parametric triangle:
        for s + t <= 1
        V(s,t) = v0 + s*(v1-v0) + t*(v2-v0)
        or V(s,t) = v0 + s*u + t*v
        result: [v0,v1,v2] ==> [v0,u,v]'''
        points = self._points.copy()

        #define a new view on the array, all v0's together
        v0s,v1s,v2s = (points[:,i,:] for i in range(3))
        np.subtract(v1,v0,out=v1)
        np.subtract(v2,v0,out=v2)
        self._parameters = points
        self._normals = np.cross(v1s,v2s)
        
    @property
    def normals(self):
      if not self._normals:
        self.create_parameters()
      return self._normals

if __name__ == '__main__':
  n = 10
  t = np.linspace(0,2*np.pi,n)

  print "Test: create segments"
  rays1 = np.zeros((n,4),dtype=np.float32)
  rays1[:,2] = np.cos(t)
  rays1[:,3] = np.sin(t)
  segs1 = Segments2d(rays1)

  rays2 =np.ones((n,4),dtype=np.float32)
  rays2[:,2] = 1+np.cos(t)
  rays2[:,3] = np.sin(t)
  segs2 = Segments2d(rays2)

  pts1,mask1 = segs1.intersection(segs2)
  pts2,mask2 = segs2.intersection(segs1)


