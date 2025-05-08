# core/__init__.py
from .gf_math import GF256, gf_add, gf_mul, gf_div, gf_inverse
from .reed_solomon import (
    rs_encode_msg,
    rs_correct_msg,
    rs_calc_syndromes,
    ReedSolomonError
)

__all__ = [
    'GF256',
    'gf_add',
    'gf_mul',
    'gf_div',
    'gf_inverse',
    'rs_encode_msg',
    'rs_correct_msg',
    'rs_calc_syndromes',
    'ReedSolomonError'
]

# Package version
__version__ = '1.0.0'