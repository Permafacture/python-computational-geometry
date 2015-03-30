'''
Result objects have the capacity to calculate
the results of intersections, etc, between
geometry objects.  Results are not calculated
until accessed, as a user may not care about all
the information possible about a result.

Result objects know what information they need
to calculate what they are asked to, and may
trigger the calculation of other properties
that are needed.

TODO
####

 Make a base result class.

 make all this less verbose! Do we really need
 four classes that have line_line_intersect in the name?

 Decide on a more consistent api.  Right now, attributes and
 dictionary keys are mixed: intersect.points[segs1].arr

'''


import numpy as np
import dimensional_utils as dimtools
from base_geometry import Param1d

class _Line_Line_Intersect(object):
    #should this derive from an ABC instead?  why?
    def __init__(self,lines0,lines1):
        super(_Line_Line_Intersect,self).__init__()

        dimfirst,dimlast = dimtools.expand_dim_first,dimtools.expand_dim_last

        if lines0.dim==1:
          self.dim_controller = {lines1:dimlast,lines0:dimfirst}
          self.axes = lines0.axes+lines1.axes 
        elif lines1.dim==1:
          self.axes = lines1.axes+lines0.axes
          self.dim_controller = {lines1:dimfirst,lines0:dimlast}
        else:
          raise ValueError("""\
             Atleast one GeometryObject must be of dimension 2
               or my head would explode.""")

        self._lines0 = lines0
        self._lines1 = lines1
        self._data = {}

    def __getitem__(self,item):
        '''If item is cached, return it.  Else, calculate the
        result, cache and return it.  Logic for result dependancy
        is handled here; getting an item may trigger the
        calculation and caching of dependancies too.'''
        try:
            return self._data.__getitem__(item)
        except KeyError:
            #not in dict, which means create this key if
            # we know how, or raise the error
            if item == self._lines0 or item == self._lines1:
                self._intersect_parameters()
            elif item == 'world':
                if self._lines0 not in self._data:
                  #intersect_parameters has not yet been called
                  #and it is a dependancy for this
                  self._intersect_parameters()
                self._intersect_points()
            else: 
              raise
            
            return self._data.__getitem__(item) 

    def __setitem__(self,key,value):
        self._data[key]=value

    def _intersect_parameters(self):
        '''create arrays representing the parameters of
        point intersection in the frame of lines0 and lines1.
           Sets self[line0] and self[lines1]''' 
        raise NotImplementedError

    def _intersect_points(self):
        '''create arrays representing the parameters of
        line shaped intersections in the frame of lines0 
        and lines1.
           Sets self[line0] and self[lines1]'''
        raise NotImplementedError


class _Line_Line_Intersect_Points(_Line_Line_Intersect):
  
    def _intersect_parameters(self):
        '''returns a list of (n,m) arrays representing 
        the parameter of intersection for lines0 and 
        lines1 of intersection for all 
        intersections between arrays of lines:
        lines0 of len n and lines1 of len m
        #TODO verify result is (n,m) and not (m,n)'''
        l0 = self._lines0
        l1 = self._lines1
        dc = self.dim_controller

        #use length 1 lines.  Complicates segments but
        #gives a consistent interface
        
        xs,ys = dimtools.xselector, dimtools.yselector
        x1,y1 = (dc[l0](l0['begin'].arr)[k] for k in (xs,ys))
        x2,y2 = (dc[l0](l0['normal'].arr)[k] for k in (xs,ys))
        x3,y3 = (dc[l1](l1['begin'].arr)[k] for k in (xs,ys))
        x4,y4 = (dc[l1](l1['normal'].arr)[k] for k in (xs,ys))

        x2=x1+x2; y2=y1+y2; x4=x3+x4; y4=y3+y4        
        #calculate intersection parameters
        den = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
        numa= (x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)
        numb= (x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)
        ua = numa/den
        ub = numb/den


        failmask = (den == 0) | (numa == 0) #co-linear or parallel
        #Work with array shape suited for Param1d
        new_shp = ua.shape+(1,)
        failmask.shape = new_shp
        ua.shape = new_shp; ub.shape=new_shp
        #apply line,ray and segment conditions to intersections
        if l0.type != 'line': failmask = failmask | (ua<0) 
        if l1.type != 'line': failmask = failmask | (ub<0)
        if l0.type == 'segment': 
          failmask = failmask | (ua>dc[l0](l0['length'].arr))
        if l1.type == 'segment': 
          failmask = failmask | (ub>dc[l1](l1['length'].arr))

        #rather than store mask, use NAN to indicate invalid
        ua[failmask] = np.nan
        ub[failmask] = np.nan

        #save results
        self[l0] = Param1d(ua,self.axes)
        self[l1] = Param1d(ub,self.axes)

    def _intersect_points(self):
        #calcuate points of intersection
        #TODO: Let line do this
        line0 = self._lines0
        ua = self[line0]
        dc = self.dim_controller[line0]
        begin = line0['begin'].arr
        normal = line0['normal'].arr
        begins = dc(begin)
        normals = dc(normal)
        test = ua.arr*normals 
        self['world'] = Vec2d(begins+test,self.axes)

class _Line_Line_Intersect_Lines(_Line_Line_Intersect):
    '''cached dict of lines from line/line intersections'''
    pass

class Result(object):
    pass

class LineLineIntersect(Result):
    '''Result object for line intersections
    implemented as a dictionary for consistency'''
    def __init__(self,lines0,lines1):
        super(LineLineIntersect,self).__init__() 
        self.points = _Line_Line_Intersect_Points(lines0,lines1)
        self.lines = _Line_Line_Intersect_Lines(lines0,lines1)
    

def dispatcher(this, that):
    if isinstance(this,Lines2d):
      pass

