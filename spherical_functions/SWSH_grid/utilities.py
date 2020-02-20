# Copyright (c) 2020, Michael Boyle
# See LICENSE file for details: <https://github.com/moble/spherical_functions/blob/master/LICENSE>

### NOTE: The functions in this file are intended purely for inclusion in the Modes class.  In
### particular, they assume that the first argument, `self` is an instance of Modes.  They should
### probably not be used outside of that class.


def modes(self, ell_max=None, **metadata):
    """Return mode weights of function decomposed into SWSHs

    This method uses `spinsfast` to convert values on an equiangular grid to mode weights.

    The output array has one less dimension than this object; rather than the last two axes giving
    the values on the two-dimensional grid, the last axis gives the mode weights.

    Parameters
    ==========
    ell_max: None or int [defaults to None]
        Maximum ell value in the output.  If None, the result will have enough ell values to express
        the data on the grid without aliasing: (max(n_phi, n_theta) - 1) // 2.
    **metadata: any types
        Additional keyword arguments are passed through to the Modes constructor on output

    """
    from .. import Modes
    import numpy as np
    import spinsfast
    ell_max = ell_max or (max(n_phi, n_theta) - 1) // 2
    return Modes(spinsfast.map2salm(self.view(np.ndarray), self.s, ell_max),
                 spin_weight=self.s, ell_min=0, ell_max=ell_max, **metadata)


def _check_broadcasting(self, array, reverse=False):
    """Test whether or not the given array can broadcast against this object"""
    import numpy as np

    if isinstance(array, type(self)):
        try:
            if reverse:
                np.broadcast(array, self)
            else:
                np.broadcast(self, array)
        except ValueError:
            return False
        else:
            return True
    else:
        try:
            if reverse:
                np.broadcast(array, self[..., 0, 0])
            else:
                np.broadcast(self[..., 0, 0], array)
        except ValueError:
            return False
        else:
            return True
