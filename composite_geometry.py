'''
Module for Geometry objects composed of points or
parameters.

TODO
####

Figure out where named axes are kept.
Right now, geometry objects and results both 
store these things.  Should be more DRY.

Make Segment2d a subclass of Line2d which calculates
its own normal only when needed.  Seg2dSeg2dIntersect
subclasses Line2dLine2dIntersect and adds it's 
extra boundry conditions.

'''
from __future__ import print_function
import numpy as np
from base_geometry import BaseGeometryObject,Vec2d,Param1d
import dimensional_utils as dimtools

class CompositeGeometryObject(BaseGeometryObject):
    '''Parent class for lines, polygons, curves, and other 
    geometries composed of points of arbitrary dimensionality.

    Keeps potentially not yet calculated BaseGeometryObjects
    (ie: cacheable) in a dictionary type interface.  

    #TODO Should be ABC mutable hash?'''

    def _additem_(self,key,value,read_only=True):
        '''Like __additem__, but checks type and initializes
        axes of object''' 

        #Do I want CompositeGeometryObject to pass this? untested!
        if isinstance(value,BaseGeometryObject):
          self._data[key] = value
        else:
          raise ValueError('Requires a GeometryObject')
        if self.axes==None:
          self.axes = value.axes
          self.dim = value.dim

    def __getitem__(self,key):
        return self._data[key]


class Lines2d(CompositeGeometryObject):
    types = ('line','ray','segment')
    def __init__(self, type='line',begin=None, 
                 end=None, normal=None,
                 axes=None,dtype=np.float64):

       super(Lines2d,self).__init__(axes,dtype)

       #logic for deciding if fundamental data needs to be
       # calculated, depending on type of line this is.
       if type in self.types:
         self.type = type
       else:
         raise ValueError('%s is not a recognized line type:%s'%(
                            type,self.types))

       assert( (end != None or normal != None) and begin != None)
       self._additem_('begin',Vec2d(begin,self.axes))

       if end != None:
         self.type ='segment'
         print ("Warning: 'end' given for non segment type.\n",
               "Coercing to segment.")
         self._additem_('end',Vec2d(end,self.axes))
         self._normalize_()
       else:
         self._normalize_()


    def _normalize_(self,dim_pts=dimtools.expand_dim_dtype):
        result = self['end'].arr-self['begin'].arr
        # Did this to save array creations, but changing
        # array structure broke it.
        #tmp = np.empty((len(end),3),dtype=end['x'].dtype)
        #tmp[:,:2] = np.square(result)
        #tmp[:,2] = np.add(tmp[:,0],tmp[:,1])
        #tmp[:,2] = np.sqrt(tmp[:,2])
        square = np.square(result)
        length = np.add(square[...,0],square[...,1])
        length = np.sqrt(length)
        self._additem_('length',Param1d(length,self.axes))
        result /= dim_pts(length)
        self._additem_('normal',Vec2d(result,self.axes))

    def eval_param(self,param_array,dimf=dimtools.expand_dim_first):
        '''for (N,M) lines, evaluate (N,M,x) parameters'''
        #TODO, may recieve a parameter object or a an ndarray
        #TODO and may need to broadcast or may not.
        # try/except?
        begin = self['begin'].arr
        normal = self['normal'].arr
        begins = begin #dimf(begin)
        normals = normal #dimf(normal)
        #test = param_array.arr*normals
        test = param_array*normals
        return Vec2d(begins+test,self.axes)
