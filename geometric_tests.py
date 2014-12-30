'''
Geometric tests between different geometry types
'''

import numpy as np


class reversible_args(object):
    '''Decorator for reversing the arguments of a geometric
    test if needed, and transposing the result if reversed'''

    def __init__(self,name1,name2):
        '''original function takes arguments of type name1
        and type name2, in that order'''
        self.name1=name1
        self.name2=name2
    def __call__(self,f):
        '''Do something to change this docstring to the
        docstring of the original function'''
        def wrapped_f(geom1,geom2):
            if geom1.name == self.name1 and geom2.name==self.name2:
              return f(geom1,geom2)
            elif geom1.name == self.name2 and geom2.name==self.name1:
              result,mask = f(geom2,geom1)
              return result.swapaxes(0,1), mask.swapaxes(0,1)
            else:
              #this should never happend
              print "there must have been a mistake in the naming of something..."
              raise NotImplemented
        wrapped_f.__doc__ = f.__doc__
        wrapped_f.__name__ = f.__name__
        return wrapped_f

@reversible_args('segments2d','segments2d')
def segments2d_intersection_segments2d(segs1,segs2):
    '''returns a (n,m,2) array representing all intersections
    between arrays of line segments segs1 (n,2) and segs2 (m,2),
    and an (n,m,1) mask to distinguish segments that did not
    intersect.'''
    r1s = segs1.data[np.newaxis,:]
    r2s = segs2.data[:,np.newaxis]
    x1,y1,x2,y2 = r1s[:,:,0],r1s[:,:,1],r1s[:,:,2],r1s[:,:,3]
    x3,y3,x4,y4 = r2s[:,:,0],r2s[:,:,1],r2s[:,:,2],r2s[:,:,3]
    
    den = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    numa= (x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)
    numb= (x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)
    ua = numa/den
    ub = numb/den
    xs = x1 + ua*(x2-x1)
    ys = y1 + ua*(y2-y1)
    #mask = (den != 0) & (numa != 0)
    mask = (ua>=0) & (ua<=1) & (ub>=0) & (ub<=1)
    xs[mask] = np.inf
    return np.array([xs,ys]).T,mask

@reversible_args('segments2d','aabbs')
def segments2d_intersects_aabb(segs,aabb):
    print "got called!",segs.name,aabb

