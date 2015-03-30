'''
Utilities to facilitate navigating the dimensionality of
numpy arrays

#TODO rename this file dimtools, because I like 
importing it as dimtools anyway.
'''

from __future__ import print_function
import numpy as np

#rather than deal with structs, x,y,z,etc are just offests in the
# array of the last dimension
xselector = (Ellipsis,0)
yselector = (Ellipsis,1)
zselector = (Ellipsis,2)


#TODO make slices to get say all of the (7,7,2) arrays for x:y
# of an (7,7,M,P,2) array.


#A common task is to apply some ufunc on two arrays and get 
#a result that has a dimensions representing each array.
#Such as an (N,x) array plus a (M,x) array gives an
#(N,M,x) array, where x is 2 for 2d points.  
#(N,O,P,2)+(M,2) => (N,O,P,M,2).  The second array must 
#always be (M,x).  dim_0 and dim_1 do this, and dim_pts
#applies (N,1) to (N,x) (scalar to x,y and z, for instance)

'''
#TODO, straighten out dimensions
# be consistent!
#currently not doing this correctly

See example:
a1 = np.ones((12,15,1))
a2 = np.ones((17,1))
dim0,dim1 = expand_dim_first, expand_dim_last
error = dim0(a1) + dim1(a2)
aresult = dim1(a1) + dim0(a2)
aresult.shape
dim1(a1).shape
'''

#TODO make dimension expansion more flexible:
# insert dimensions into middle, etc.

def expand_dim_first(arr):
    '''dim_first(arr(shape=(N,M,2))) + dim_last(arr2(shape=(P,2)))
    => arr_result(shape=(N,M,P,2))'''
    assert(isinstance(arr,np.ndarray))
    return np.expand_dims(arr,axis=0)

def expand_dim_last(arr):
    '''dim_first(arr(shape=(N,M,2))) + dim_last(arr2(shape=(P,2)))
    => arr_result(shape=(N,M,P,2)). Arr must be (P,x) where
    x is 2 for 2d point, etc.'''
    assert(isinstance(arr,np.ndarray))
    return np.expand_dims(arr,axis=-2)

def expand_dim_dtype(arr):
    ''' (N,M,x) + dim_pts((N,M,1)) to apply
    scalar to vector'''
    assert(isinstance(arr,np.ndarray))
    return np.expand_dims(arr,axis=-1)

