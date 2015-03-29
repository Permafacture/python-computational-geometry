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
        self._type1=name1
        self._type2=name2
    def __call__(self,f):
        '''Do something to change this docstring to the
        docstring of the original function'''
        def wrapped_f(geom1,geom2):
            if geom1._type == self._type1 and geom2._type==self._type2:
              return f(geom1,geom2)
            elif geom1._type == self._type2 and geom2._type==self._type1:
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
    r1s = segs1._points[np.newaxis,:]
    r2s = segs2._points[:,np.newaxis]
    x1,y1,x2,y2 = r1s[:,:,0],r1s[:,:,1],r1s[:,:,2],r1s[:,:,3]
    x3,y3,x4,y4 = r2s[:,:,0],r2s[:,:,1],r2s[:,:,2],r2s[:,:,3]
    
    den = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    numa= (x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)
    numb= (x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)
    ua = numa/den
    ub = numb/den
    xs = x1 + ua*(x2-x1)
    ys = y1 + ua*(y2-y1)
    mask = (den != 0) & (numa != 0)
    mask = (ua>=0) & (ua<=1) & (ub>=0) & (ub<=1)
    xs[mask] = np.inf
    return np.array([xs,ys]).T,mask

@reversible_args('segments3d','triangles')
def segments3d_intersection_triangles(segs,tri):
    '''http://geomalgorithms.com/a06-_intersect-2.html#intersect3D_RayTriangle%28%29'''

    '''
    #define SMALL_NUM   0.00000001 // anything that avoids division overflow
    // dot product (3D) which allows vector operations in arguments
    #define dot(u,v)   ((u).x * (v).x + (u).y * (v).y + (u).z * (v).z)
     


    // intersect3D_RayTriangle(): find the 3D intersection of a ray with a triangle
    //    Input:  a ray R, and a triangle T
    //    Output: *I = intersection point (when it exists)
    //    Return: -1 = triangle is degenerate (a segment or point)
    //             0 =  disjoint (no intersect)
    //             1 =  intersect in unique point I1
    //             2 =  are in the same plane
    int
    intersect3D_RayTriangle( Ray R, Triangle T, Point* I )
    {
        Vector    u, v, n;              // triangle vectors
        Vector    dir, w0, w;           // ray vectors
        float     r, a, b;              // params to calc ray-plane intersect

        // get triangle edge vectors and plane normal
        u = T.V1 - T.V0;
        v = T.V2 - T.V0;
        n = u * v;              // cross product
        if (n == (Vector)0)             // triangle is degenerate
            return -1;                  // do not deal with this case

        dir = R.P1 - R.P0;              // ray direction vector
        w0 = R.P0 - T.V0;
        a = -dot(n,w0);
        b = dot(n,dir);
        if (fabs(b) < SMALL_NUM) {     // ray is  parallel to triangle plane
            if (a == 0)                 // ray lies in triangle plane
                return 2;
            else return 0;              // ray disjoint from plane
        }

        // get intersect point of ray with triangle plane
        r = a / b;
        if (r < 0.0)                    // ray goes away from triangle
            return 0;                   // => no intersect
        // for a segment, also test if (r > 1.0) => no intersect

        *I = R.P0 + r * dir;            // intersect point of ray and plane

        // is I inside T?
        float    uu, uv, vv, wu, wv, D;
        uu = dot(u,u);
        uv = dot(u,v);
        vv = dot(v,v);
        w = *I - T.V0;
        wu = dot(w,u);
        wv = dot(w,v);
        D = uv * uv - uu * vv;

        // get and test parametric coords
        float s, t;
        s = (uv * wv - vv * wu) / D;
        if (s < 0.0 || s > 1.0)         // I is outside T
            return 0;
        t = (uv * wu - uu * wv) / D;
        if (t < 0.0 || (s + t) > 1.0)  // I is outside T
            return 0;

        return 1;                       // I is in T
    }
     '''
@reversible_args('segments2d','aabbs')
def segments2d_intersects_aabb(segs,aabb):
    print "got called!",segs._type,aabb

