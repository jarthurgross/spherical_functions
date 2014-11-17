# Copyright (c) 2014, Michael Boyle
# See LICENSE file for details: <https://github.com/moble/spherical_functions/blob/master/LICENSE>

from __future__ import print_function, division, absolute_import

__all__ = ['Wigner3j', 'Wigner_D_element', 'Wigner_D_matrices', 'SWSH',
           'factorial', 'binomial_coefficient', 'ladder_operator_coefficient']

from numpy import array, empty, floor
from math import factorial, sqrt
from sys import float_info

from quaternion.numba_wrapper import njit, xrange

## Module constants
ell_max = 32
epsilon = 1.e-15
min_exp = float_info.min_exp
mant_dig = float_info.mant_dig
error_on_bad_indices = True

## Factorial
factorials = array([float(factorial(i)) for i in range(171)])
@njit('f8(i8)')
def factorial(i):
    return factorials[i]


## Binomial coefficients
_binomial_coefficients = array([floor(0.5+factorials[n]/(factorials[k]*factorials[n-k]))
                                for n in range(2*ell_max+1) for k in range(n+1)])
@njit('f8(i8,i8)')
def binomial_coefficient(n,k):
    return _binomial_coefficients[(n*(n+1))//2+k]


## Ladder-operator coefficients
_ladder_operator_coefficients = array([sqrt(ell*(ell+1)-m*(m+1))
                                       for ell in range(ell_max+1) for m in range(-ell,ell+1)])
@njit('f8(i8,i8)')
def ladder_operator_coefficient(ell,m):
    return _ladder_operator_coefficients[ell*(ell+1)+m]


## Coefficients used in constructing the Wigner D matrices
_Wigner_coefficients = array([sqrt( factorials[ell+m]*factorials[ell-m] / (factorials[ell+mp]*factorials[ell-mp] ) )
                              for ell in range(ell_max+1)
                              for mp in range(-ell, ell+1)
                              for m in range(-ell, ell+1) ])
@njit('f8(i8,i8,i8)')
def _Wigner_coefficient(ell,mp,m):
    return _Wigner_coefficients[ell*(ell*(4*ell + 6) + 5)//3 + mp*(2*ell + 1) + m]


@njit('i8(i8,i8,i8)')
def _Wigner_index(ell,mp,m):
    return ell*(ell*(4*ell + 6) + 5)//3 + mp*(2*ell + 1) + m

def LM_range(ell_min, ell_max):
    """Array of (ell,m) indices in standard order

    This function returns an array of essentially

    [[ell,m] for ell in range(ell_min, ell_max+1)
             for m in range(-ell,ell+1)]

    This is, for example, the order assumed for mode data in the `waveforms`
    module.

    """
    # # Sympy commands to calculate the total size:
    # from sympy import symbols, summation
    # ell_min,ell,ell_max = symbols('ell_min,ell,ell_max', integer=True)
    # summation((2*ell + 1), (ell, ell_min, ell_max))
    LM = empty((ell_max*(ell_max+2) - ell_min**2 + 1,2), dtype=int)
    _LM_range(ell_min, ell_max, LM)
    return LM
@njit('void(i8,i8,i8[:,:])')
def _LM_range(ell_min, ell_max, LM):
    i=0
    for ell in xrange(ell_min,ell_max+1):
        for m in xrange(-ell,ell+1):
            LM[i,0] = ell
            LM[i,1] = m
            i+=1
@njit('i8(i8,i8,i8)')
def LM_index(ell, m, ell_min):
    """Array index for given (ell,m) mode

    Assuming an array of

    [[ell,m] for ell in range(ell_min, ell_max+1)
             for m in range(-ell,ell+1)]

    this function returns the index of the (ell,m) element.  (Note that
    ell_max doesn't actually come into this calculation, so it is not taken
    as an argument to the function.)

    This can be calculated in sympy as

      from sympy import symbols, summation
      ell,m,ell_min, = symbols('ell,m,ell_min,', integer=True)
      summation(2*ell + 1, (ell, ell_min, ell-1)) + (ell+m)

    """
    return ell*(ell+1) - ell_min**2 + m
@njit('i8(i8,i8)')
def LM_total_size(ell_min, ell_max):
    """Total array size of (ell,m) components

    Assuming an array of

    [[ell,m] for ell in range(ell_min, ell_max+1)
             for m in range(-ell,ell+1)]

    this function returns the total size of that array.

    This can be calculated in sympy as

      from sympy import symbols, summation
      ell,ell_min,ell_max = symbols('ell,ell_min,ell_max', integer=True)
      summation(2*ell + 1, (ell, ell_min, ell_max))

    """
    return ell_max*(ell_max+2) - ell_min**2 + 1

def LMpM_range(ell_min, ell_max):
    """Array of (ell,mp,m) indices in standard order

    This function returns an array of essentially

    [[ell,mp,m] for ell in range(ell_min, ell_max+1)
                for mp in range(-ell,ell+1)
                for m in range(-ell,ell+1)]

    This is, for instance, the array of indices of the Wigner D matrices
    constructed by this module.

    """
    # # Sympy commands to calculate the total size:
    # from sympy import symbols, summation
    # ell_min,ell,ell_max = symbols('ell_min,ell,ell_max', integer=True)
    # summation((2*ell + 1)**2, (ell, ell_min, ell_max))
    LMpM = empty(((ell_max*(11 + ell_max*(12 + 4*ell_max)) + ell_min*(1 - 4*ell_min**2) + 3) // 3, 3), dtype=int)
    _LMpM_range(ell_min, ell_max, LMpM)
    return LMpM
@njit('void(i8,i8,i8[:,:])')
def _LMpM_range(ell_min, ell_max, LMpM):
    i=0
    for ell in xrange(ell_min,ell_max+1):
        for mp in xrange(-ell,ell+1):
            for m in xrange(-ell,ell+1):
                LMpM[i,0] = ell
                LMpM[i,1] = mp
                LMpM[i,2] = m
                i+=1
@njit('i8(i8,i8,i8,i8)')
def LMpM_index(ell, mp, m, ell_min):
    """Array index for given (ell,mp,m) mode

    Assuming an array (e.g., Wigner D matrices) in the order

    [[ell,mp,m] for ell in range(ell_min, ell_max+1)
                for mp in range(-ell,ell+1)
                for m in range(-ell,ell+1)]

    this function returns the index of the (ell,mp,m) element.  (Note that
    ell_max doesn't actually come into this calculation, so it is not taken
    as an argument to the function.)

    This can be calculated in sympy as

      from sympy import symbols, summation
      ell,mp,m,ell_min, = symbols('ell,mp,m,ell_min,', integer=True)
      summation((2*ell + 1)**2, (ell, ell_min, ell-1)) + (2*ell+1)*(ell+mp) + (ell+m)

    """
    # raw output is: 4*ell**3/3 + 2*ell**2 + 2*ell*mp + 5*ell/3 - 4*ell_min**3/3 + ell_min/3 + m + mp
    # We rearrange that to act more nicely
    return (((4*ell + 6)*ell + 6*mp + 5)*ell + ell_min*(1- 4*ell_min**2) + 3*(m + mp)) // 3
@njit('i8(i8, i8)')
def LMpM_total_size(ell_min, ell_max):
    """Total array size of Wigner D matrix

    Assuming an array (e.g., Wigner D matrices) in the order

    [[ell,mp,m] for ell in range(ell_min, ell_max+1)
                for mp in range(-ell,ell+1)
                for m in range(-ell,ell+1)]

    this function returns the total size of that array.

    This can be calculated in sympy as

      from sympy import symbols, summation
      ell,ell_min,ell_max = symbols('ell,ell_min,ell_max', integer=True)
      summation((2*ell + 1)**2, (ell, ell_min, ell_max))

    """
    # raw output is: 4*ell_max**3/3 + 4*ell_max**2 + 11*ell_max/3 - 4*ell_min**3/3 + ell_min/3 + 1
    # We rearrange that to act more nicely
    return (((4*ell_max + 12)*ell_max + 11)*ell_max + (-4*ell_min**2 + 1)*ell_min + 3) // 3


from .Wigner3j import Wigner3j
from .WignerD import (Wigner_D_element, _Wigner_D_element,
                      Wigner_D_matrices, _Wigner_D_matrices,
                      _linear_matrix_index, _linear_matrix_diagonal_index,
                      _linear_matrix_offset, _total_size_D_matrices)
from .SWSH import SWSH, _SWSH # sYlm, Ylm
