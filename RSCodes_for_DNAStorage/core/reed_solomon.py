#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reed-Solomon Codec for DNA Storage
- GF(256) implementation using 0x11D polynomial
- Optimized for nucleotide byte sequences
"""

from .gf_math import gf, GF256
from .exceptions import ReedSolomonError


class ReedSolomon:
    def __init__(self, nsym=10, fcr=0, generator=2):
        """
        Initialize RS codec with DNA storage defaults
        :param nsym: Number of ECC symbols (default 10)
        :param fcr: First consecutive root (default 0)
        :param generator: Field generator (default 2)
        """
        self.nsym = nsym
        self.fcr = fcr
        self.generator = generator
        self.gf = GF256()  # Shared GF256 instance

    def rs_generator_poly(self):
        """Generate the Reed-Solomon generator polynomial"""
        g = [1]
        for i in range(self.nsym):
            term = [1, self.gf.pow(self.generator, i + self.fcr)]
            g = self.gf.poly_mul(g, term)
        return g

    def rs_encode_msg(self, msg_in):
        """
        Encode message with RS ECC
        :param msg_in: Input message as bytearray
        :return: Encoded message (message + ECC)
        """
        if len(msg_in) + self.nsym > 255:
            raise ReedSolomonError("Message too long for GF(256)")

        # Pad with zeros and divide by generator polynomial
        _, remainder = self.gf.poly_div(
            msg_in + [0] * self.nsym,
            self.rs_generator_poly()
        )

        return msg_in + remainder

    def rs_calc_syndromes(self, msg):
        """Calculate syndromes polynomial"""
        synd = [0] * self.nsym
        for i in range(self.nsym):
            synd[i] = self.gf.poly_eval(msg, self.gf.pow(self.generator, i + self.fcr))
        return [0] + synd  # Pad with 0 for mathematical precision

    def rs_correct_errata(self, msg, synd, err_pos):
        """Correct errors at known positions"""
        coef_pos = [len(msg) - 1 - p for p in err_pos]
        err_loc = self.rs_find_errata_locator(coef_pos)
        err_eval = self.rs_find_error_evaluator(synd[::-1], err_loc, len(err_loc) - 1)[::-1]

        X = []  # Error positions
        for i in range(len(coef_pos)):
            l = 255 - coef_pos[i]
            X.append(self.gf.pow(self.generator, -l))

        E = [0] * len(msg)
        for i, Xi in enumerate(X):
            Xi_inv = self.gf.inverse(Xi)
            err_loc_prime = 1
            for j in range(len(X)):
                if i != j:
                    err_loc_prime = self.gf.mul(err_loc_prime,
                                                self.gf.sub(1, self.gf.mul(Xi_inv, X[j])))

            y = self.gf.poly_eval(err_eval[::-1], Xi_inv)
            y = self.gf.mul(self.gf.pow(Xi, 1 - self.fcr), y)

            magnitude = self.gf.div(y, err_loc_prime)
            E[err_pos[i]] = magnitude

        return self.gf.poly_add(msg, E)

    def rs_find_error_locator(self, synd, erase_loc=None, erase_count=0):
        """Find error locator polynomial using Berlekamp-Massey"""
        if erase_loc:
            err_loc = list(erase_loc)
            old_loc = list(erase_loc)
        else:
            err_loc = [1]
            old_loc = [1]

        synd_shift = len(synd) - self.nsym if len(synd) > self.nsym else 0

        for i in range(self.nsym - erase_count):
            K = erase_count + i + synd_shift if erase_loc else i + synd_shift
            delta = synd[K]
            for j in range(1, len(err_loc)):
                delta ^= self.gf.mul(err_loc[-(j + 1)], synd[K - j])

            old_loc = old_loc + [0]

            if delta != 0:
                if len(old_loc) > len(err_loc):
                    new_loc = self.gf.poly_scale(old_loc, delta)
                    old_loc = self.gf.poly_scale(err_loc, self.gf.inverse(delta))
                    err_loc = new_loc
                err_loc = self.gf.poly_add(err_loc, self.gf.poly_scale(old_loc, delta))

        while len(err_loc) and err_loc[0] == 0:
            del err_loc[0]

        errs = len(err_loc) - 1
        if (errs - erase_count) * 2 + erase_count > self.nsym:
            raise ReedSolomonError("Too many errors to correct")

        return err_loc

    def rs_find_errors(self, err_loc, nmess):
        """Find error positions using Chien search"""
        err_pos = []
        for i in range(nmess):
            if self.gf.poly_eval(err_loc, self.gf.pow(self.generator, i)) == 0:
                err_pos.append(nmess - 1 - i)
        if len(err_pos) != len(err_loc) - 1:
            raise ReedSolomonError("Error locator degree mismatch")
        return err_pos

    def rs_correct_msg(self, msg_in, erase_pos=None):
        """
        Correct errors in message
        :param msg_in: Received message (message + ECC)
        :param erase_pos: Optional list of erasure positions
        :return: (corrected_message, ecc_remainder)
        """
        if erase_pos is None:
            erase_pos = []

        if len(msg_in) > 255:
            raise ReedSolomonError("Message too long for GF(256)")

        msg_out = list(msg_in)
        for e in erase_pos:
            msg_out[e] = 0

        synd = self.rs_calc_syndromes(msg_out)
        if max(synd) == 0:
            return msg_out[:-self.nsym], msg_out[-self.nsym:]

        fsynd = self.rs_forney_syndromes(synd, erase_pos, len(msg_out))
        err_loc = self.rs_find_error_locator(fsynd, erase_count=len(erase_pos))
        err_pos = self.rs_find_errors(err_loc[::-1], len(msg_out))

        if not err_pos:
            raise ReedSolomonError("Could not locate errors")

        msg_out = self.rs_correct_errata(msg_out, synd, erase_pos + err_pos)
        synd = self.rs_calc_syndromes(msg_out)
        if max(synd) > 0:
            raise ReedSolomonError("Decoding failed")

        return msg_out[:-self.nsym], msg_out[-self.nsym:]

    # Helper methods would follow...