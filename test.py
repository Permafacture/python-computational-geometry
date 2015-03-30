'''Multidimensional numpy arrays with geometry datatypes 
and named fields/axes for queries and aggregation.

aggregation (like sum and argmin) happens on named axes'''
from __future__ import print_function
import numpy as np
import dimensional_utils as dimtools
'''
Thoughts
########

We have collections of arrays that share a base dtype, though
attributes may be mixed lines, points and other.  How to assert 
and access this?   Giving GeometryObject a base_type attribute 
right now.

Would love to have these be sparse arrays.  Would that be 
possible?  How to expand dimesnions and apply as if they
were non-sparse arrays?
 
Using a custom dtype would simplify dimensional utils, but would
complicate ufuncs. Just deal with it in dimtools and hope the
user only wants to use provided dimtools? Cast back and forth?
Subclass ndarray (the hardest, most scary option)

TODO 
####

get rid of result.intersects['world']. return only parameters
and let Line2d have a method for resolving those parameters into points.
or atleast let the result just use the geometry object do the
evaluation of its own parameters

Put dim_controller, axes, etc in either the result or some base 
object that Result and all geometry objects inherit from.

Use masked arrays.  They behave better than leaving NaN's in an
array and using nanargmax, etc.  Maybe?

limitations
###########
  GeometryObject collections must be arrays of all the same dtype.
  That is, different parameters/vectors must all be float32 or 64
  But that's an okay thing I think.

'''
def export4mpl(thing):
    '''batch data for Matplotlib for faster drawing'''
    xs,ys = dimtools.xselector,dimtools.yselector
    if isinstance(thing,Lines2d):
        segs=thing
        begin = segs['begin'].arr
        end = segs['end'].arr
        mask = ~np.isnan(begin[xs])
        mplxs = [None]*(3*np.sum(mask))
        mplys = mplxs[:]
        mplxs[::3] = begin[xs][mask]
        mplxs[1::3] = end[xs][mask]
        mplys[::3] = begin[ys][mask]
        mplys[1::3] = end[ys][mask]
    elif isinstance(thing,Vec2d):
        vec = thing.arr
        mask = ~np.isnan(vec[xs])
        mplxs = [None]*(2*np.sum(mask))
        mplys = mplxs[:]
        mplxs[::2] = vec[xs][mask]
        mplys[::2] = vec[ys][mask]
    elif isinstance(thing,np.ndarray):
        #must be an array of points
        mask = ~np.isnan(thing[xs])
        mplxs = [None]*(2*np.sum(mask))
        mplys = mplxs[:]
        mplxs[::2] = thing[xs][mask]
        mplys[::2] = thing[ys][mask]
        
        
    else:
       raise NotImplementedError(
          "%s Not known type to batch"%type(thing))
    return mplxs,mplys


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from composite_geometry import Lines2d
    from base_geometry import Vec2d
    from results import LineLineIntersect

    #One dimensional collection of lines
    n = 5 
    begins1 = np.random.randint(-25,25,(n,2))
    ends1 = np.random.randint(-25,25,(n,2))
    segs1 = Lines2d(begin=begins1,end=ends1)

    #More complicated collection of lines
    m=7  
    begins2 = np.random.randint(-25,25,(m,m,2))
    ends2 =np.random.randint(-25,25,(m,m,2))
    segs2 = Lines2d(begin=begins2,end=ends2)


    #plot segments
    xs,ys = export4mpl(segs1)
    plt.plot(xs,ys,'b') #blue solid
    xs,ys = export4mpl(segs2)
    plt.plot(xs,ys,color='.70') #gray dashed
    
    xs,ys = export4mpl(segs2['begin'])
    plt.plot(xs,ys,'ko') #black dots

    #Set up result, but don't calculate
    result = LineLineIntersect(segs1,segs2)

    #plot all intersections
    #pts = result.points['world']
    #xs,ys =export4mpl(pts) 
    #plt.plot(xs,ys,'ro')

    ###plot segs1 from begining to first intersection###
    
    ub = result.points[segs2]

    axis = 2
    shortest = np.nanmin(ub.arr,axis=axis)
    pts = segs2.eval_param(shortest)

    ##plot all first intersections
    ##xs,ys =export4mpl(pts) 
    ##plt.plot(xs,ys,'ro')
    

    #plot the lines from begining to first intersection.
    short_lines = Lines2d(begin=segs2['begin'].arr, end=pts.arr)
    xs,ys =export4mpl(short_lines) 
    plt.plot(xs,ys,'g') #solid green
    plt.show()

"""
    Don;t remember what this does.  maybe it'll come up again.
    #TODO? Select points directly from results
    #http://stackoverflow.com/questions/5798364/using-numpy-argmax-on-multidimensional-arrays
    u = np.ma.MaskedArray(ua.arr,np.isnan(ua.arr))

    axis = 2
    shortest = np.argmin(u,axis=axis)
    selector = np.indices(result.points['world'].arr.shape)    

    #tup = np.indices(shortest.shape)
    #selector = tup[:axis] + (shortest,) + tup[axis:-1]
    #selector = selector + (tup[-1] + np.array([0,1]),)

    selector[Ellipsis,0] = shortest
    selector[Ellipsis,1] = shortest

    begins = segs2['begin'].arr
    first_intersects =result.points['world'].arr[selector] 
    short_lines = Lines2d(begin=begins,end=first_intersects) 
    # xs,ys = export4mpl(first_intersects)
    # plt.plot(xs,ys,'ro')
"""
