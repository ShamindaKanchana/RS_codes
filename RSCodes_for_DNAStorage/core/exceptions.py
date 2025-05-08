#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom Exceptions for Reed-Solomon DNA Storage System
"""

class ReedSolomonError(Exception):
    """Base exception for all RS codec errors"""
    def __init__(self, message="Reed-Solomon error occurred"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"RS Error: {self.message}"

class InputTooLongError(ReedSolomonError):
    """Raised when input exceeds GF(256) field capacity"""
    def __init__(self, max_length=255):
        super().__init__(
            f"Message too long for GF(256). Max length: {max_length} bytes"
        )
        self.max_length = max_length

class TooManyErrorsError(ReedSolomonError):
    """Raised when errors exceed correction capability"""
    def __init__(self, nsym, errors_found):
        super().__init__(
            f"Too many errors ({errors_found}) for {nsym} ECC symbols. "
            f"Max correctable: {nsym//2}"
        )
        self.nsym = nsym
        self.errors_found = errors_found

class DecodingFailureError(ReedSolomonError):
    """Raised when decoding fails to correct errors"""
    def __init__(self, residual_errors):
        super().__init__(
            f"Decoding failed. Residual errors detected: {residual_errors}"
        )
        self.residual_errors = residual_errors

class InvalidNucleotideError(ReedSolomonError):
    """Raised when invalid nucleotide values are encountered"""
    def __init__(self, invalid_value):
        super().__init__(
            f"Invalid nucleotide value: {invalid_value}. "
            "Must be in [0x00, 0x01, 0x02, 0x03] (A,T,G,C)"
        )
        self.invalid_value = invalid_value

class DNAConstraintViolationError(ReedSolomonError):
    """Raised when DNA storage constraints are violated"""
    def __init__(self, constraint_type, details):
        super().__init__(
            f"DNA constraint violation ({constraint_type}): {details}"
        )
        self.constraint_type = constraint_type
        self.details = details