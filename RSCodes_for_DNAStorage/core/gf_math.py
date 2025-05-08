#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Galois Field (GF256) Arithmetic Module
- Optimized for Reed-Solomon in DNA storage systems
- Uses standard polynomial 0x11D (x^8 + x^4 + x^3 + x^2 + 1)
"""

import time


class GF256:
    def __init__(self, prim_poly=0x11D):
        """Initialize GF(256) with precomputed log/antilog tables"""
        self.prim_poly = prim_poly
        self.gf_exp = [0] * 512  # Anti-log table
        self.gf_log = [0] * 256  # Log table
        self._init_tables()

    def __repr__(self):
        return f"GF256(prim_poly=0x{self.prim_poly:X})"

    def _init_tables(self):
        """Precompute logarithm and anti-log tables"""
        x = 1
        for i in range(255):
            self.gf_exp[i] = x
            self.gf_log[x] = i
            x = self._gf_mult_noLUT(x, 2)

        self.gf_exp[255:510] = self.gf_exp[0:255]
        self.gf_exp[510] = 1  # Redundancy

    def _gf_mult_noLUT(self, x, y):
        """Russian Peasant Multiplication in GF(256)"""
        r = 0
        while y:
            if y & 1:
                r ^= x
            y >>= 1
            x <<= 1
            if x & 0x100:
                x ^= self.prim_poly
        return r

    # Core GF Operations
    def add(self, a, b): return a ^ b
    def sub(self, a, b): return a ^ b

    def mul(self, a, b):
        if a == 0 or b == 0: return 0
        return self.gf_exp[(self.gf_log[a] + self.gf_log[b]) % 255]

    def div(self, a, b):
        if b == 0: raise ZeroDivisionError("Division by zero in GF(256)")
        if a == 0: return 0
        return self.gf_exp[(self.gf_log[a] - self.gf_log[b]) % 255]

    def pow(self, x, power):
        if x == 0: return 0
        return self.gf_exp[(self.gf_log[x] * power) % 255]

    def inverse(self, x):
        if x == 0: raise ZeroDivisionError("No inverse for 0 in GF(256)")
        return self.gf_exp[255 - self.gf_log[x]]

    def benchmark(self, loops=10**6):
        start = time.time()
        for _ in range(loops):
            _ = self.mul(123, 231)
        print(f"Benchmark: {loops} multiplications in {time.time() - start:.3f} sec")

    @staticmethod
    def run_self_tests():
        gf = GF256()

        # Add/Sub Test
        assert gf.add(12, 23) == 12 ^ 23
        assert gf.sub(12, 23) == 12 ^ 23

        # Mul/Div Test
        for a in range(1, 256):
            for b in range(1, 256):
                assert gf.div(gf.mul(a, b), a) == b

        # Pow/Inverse Test
        for a in range(1, 256):
            assert gf.mul(a, gf.inverse(a)) == 1

        print("All GF256 self-tests passed!")


# Singleton instance
gf = GF256()
# ---- Only Runs If Executed Directly ----
if __name__ == "__main__":
    print("Running GF256 Self-Tests...")
    GF256.run_self_tests()
    print("Running GF256 Benchmark...")
    GF256().benchmark(loops=10**5)
