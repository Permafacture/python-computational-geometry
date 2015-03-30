'''
Base geometry objects are 1d, 2d, 3d, etc arrays of dtype=
default_dtype, representing parameters or vectors.

Objects have named axes that represent the geometries
that came together to create this geometry collection
(ie, in a result, each axis represents a different
geometry collection)

TODO
####

Name them consistently 

define base_dtype (float64, float32) here, yet let the user
change the base dtype.  Maybe that should be in a settings
file actually... (use dtype=None keyword assignment in init)

find a way to give more clear access to the wrapped array.
  bgo.arr kind of sucks.  subclass ndarray? But then every
  ufunc will have more object creation overhead...

'''
from __future__ import print_function
import numpy as np

class BaseGeometryObject(object):  #TODO ABC mutable mapping
    '''BaseGeometryObjects hold a self.arr of shape (N,x),
    know the names of their axes, and can be keys in dicts '''

    def __init__(self,axes=None,dtype=np.float64):
        '''sets axes.  If axes names not given, name after self.
        If contained arrays are multi dimensional and 
        no axes given, axes will all be self.
        '''

        #if axes aren't given, figure them out on first _additem_
        if type(axes) == list:
          self.dim = len(axes)
        else:
          self.dim=None
        self.axes = axes

        self.dtype = dtype
        self._cachedkeys = []
        self._data = {}

    def __hash__(self):
        '''makes object hashable for dicts.  Only this object
        and not a copy or "equal" object will do as a key'''
        return id(self)

    def __eq__(self,other):
        return id(self) == id(other)

    def _setarr(self,value,read_only=True):
        '''sets the arr attribute, coercing to an array of the 
        correct dtype if necessary'''


        if isinstance(value,np.ndarray) and value.dtype==self.dtype:
          value.flags.writeable = not read_only
          self.arr = value
        else:
          self.arr = self._coerce_to_dtype(value,
                                      read_only=read_only)
        if self.dim == None:
          self.dim = len(self.arr.shape)-1 #last dim is x,y
          self.axes = [self]*self.dim

    def _coerce_to_dtype(self,arr,read_only=True):
        '''Returns a numpy array of dtype=self.dtype from 
        a list or differently typed numpy.ndarray'''
        #using base_dtype: this should be a method now
        ret = np.array(arr,dtype=self.dtype)
        if read_only:
            ret.flags.writeable=False
        return ret

class Param1d(BaseGeometryObject):
    def __init__(self,param=None,axes=None,dtype=np.float64):
        if param==None:
            raise ValueError(
                    "param must be a np.array or iterable")
        super(Param1d,self).__init__(axes,dtype)
        self._setarr(param)
        shp = self.arr.shape
        if shp[-1] != 1 or len(shp) == 1:
          #For consistancy, give this parameter a structure
          # like a more complicated data type: [[u1],[u2]...]]
          new_shp = shp + (1,)
          self.arr = self.arr.reshape(new_shp)

class Vec2d(BaseGeometryObject):
    def __init__(self,vector=None,axes=None,dtype=np.float64):
        if vector==None:
            raise ValueError(
                    "vector must be a np.array or iterable")
        super(Vec2d,self).__init__(axes,dtype)
        self._setarr(vector)

