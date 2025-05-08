# Global variables for Galois Field exponential and logarithm tables
gf_exp = [0] * 512 
gf_log = [0] * 256

def init_tables(prim=0x11d):
    '''Precompute the logarithm and anti-log tables for faster computation later, using the provided primitive polynomial.'''
    global gf_exp, gf_log
    
    # Manually implement carry-less multiplication to avoid circular import
    def cl_mult(x, y):
        z = 0
        i = 0
        while (y >> i) > 0:
            if y & (1 << i):
                z ^= x << i
            i += 1
        return z
    
    # For each possible value in the galois field 2^8, we will pre-compute the logarithm and anti-logarithm (exponential) of this value
    x = 1
    for i in range(0, 255):
        gf_exp[i] = x # compute anti-log for this value and store it in a table
        gf_log[x] = i # compute log at the same time
        
        # Multiply x by 2 using carry-less multiplication
        x = cl_mult(x, 2)
        if x >= 256:
            x ^= prim

    # Optimization: double the size of the anti-log table 
    for i in range(255, 512):
        gf_exp[i] = gf_exp[i - 255]
    
    return gf_exp, gf_log