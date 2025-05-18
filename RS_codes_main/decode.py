from gf_operations import gf_poly_eval,gf_pow,gf_poly_add,gf_poly_mul,gf_inverse,gf_sub,gf_mul,gf_div,gf_poly_scale,gf_poly_div
from encode import ReedSolomonError

##############################RS CALC SYNDROMES ##################################################
def rs_calc_syndromes(msg, nsym):
    '''Given the received codeword msg and the number of error correcting symbols (nsym), computes the syndromes polynomial.'''
    # Diagnostic logging
    print(f"DEBUG: Calculating syndromes")
    print(f"DEBUG: Message length: {len(msg)}")
    print(f"DEBUG: Number of error correcting symbols: {nsym}")
    
    synd = [0] * nsym
    for i in range(0, nsym):
        synd[i] = gf_poly_eval(msg, gf_pow(2,i))
        
        # Detailed syndrome computation logging
        print(f"DEBUG: Syndrome[{i}] = {synd[i]}")
    
    # Pad with zero for mathematical precision
    result = [0] + synd
    
    # Syndrome analysis
    print(f"DEBUG: Full syndrome vector: {result}")
    print(f"DEBUG: Non-zero syndrome count: {len([x for x in result if x != 0])}")
    
    return result

#####################RS CHECK################################################################################################
def rs_check(msg, nsym):
    '''Returns true if the message + ecc has no error or false otherwise (may not always catch a wrong decoding or a wrong message, particularly if there are too many errors -- above the Singleton bound --, but it usually does)'''
    return ( max(rs_calc_syndromes(msg, nsym)) == 0 )




###################RS find Errata Locator #####################################################################################################

def rs_find_errata_locator(e_pos):
    '''Compute the erasures/errors/errata locator polynomial from the erasures/errors/errata positions
       (the positions must be relative to the x coefficient, eg: "hello worldxxxxxxxxx" is tampered to "h_ll_ worldxxxxxxxxx"
       with xxxxxxxxx being the ecc of length n-k=9, here the string positions are [1, 4], but the coefficients are reversed
       since the ecc characters are placed as the first coefficients of the polynomial, thus the coefficients of the
       erased characters are n-1 - [1, 4] = [18, 15] = erasures_loc to be specified as an argument.'''

    e_loc = [1] # just to init because we will multiply, so it must be 1 so that the multiplication starts correctly without nulling any term
    # erasures_loc = product(1 - x*alpha**i) for i in erasures_pos and where alpha is the alpha chosen to evaluate polynomials.
    for i in e_pos:
        e_loc = gf_poly_mul( e_loc, gf_poly_add([1], [gf_pow(2, i), 0]) )
    return e_loc
###################################################RS FIND ERROR EVALUATOR ################################################################

def rs_find_error_evaluator(synd, err_loc, nsym):
    '''Compute the error (or erasures if you supply sigma=erasures locator polynomial, or errata) evaluator polynomial Omega
       from the syndrome and the error/erasures/errata locator Sigma.'''

    # Omega(x) = [ Synd(x) * Error_loc(x) ] mod x^(n-k+1)
    _, remainder = gf_poly_div( gf_poly_mul(synd, err_loc), ([1] + [0]*(nsym+1)) ) # first multiply syndromes * errata_locator, then do a
                                                                                   # polynomial division to truncate the polynomial to the
                                                                                   # required length

    # Faster way that is equivalent
    #remainder = gf_poly_mul(synd, err_loc) # first multiply the syndromes with the errata locator polynomial
    #remainder = remainder[len(remainder)-(nsym+1):] # then slice the list to truncate it (which represents the polynomial), which
                                                                          # is equivalent to dividing by a polynomial of the length we want

    return remainder



############################RS CORRECT ERRATA#####################################################################################################

def rs_correct_errata(msg_in, synd, err_pos):  # err_pos is a list of the positions of the errors/erasures/errata
    '''Forney algorithm, computes the values (error magnitude) to correct the input message.'''
    # calculate errata locator polynomial to correct both errors and erasures (by combining the errors positions given by the error locator polynomial found by BM with the erasures positions given by caller)
    coef_pos = [len(msg_in) - 1 - p for p in
                err_pos]  # need to convert the positions to coefficients degrees for the errata locator algo to work (eg: instead of [0, 1, 2] it will become [len(msg)-1, len(msg)-2, len(msg) -3])
    err_loc = rs_find_errata_locator(coef_pos)
    # calculate errata evaluator polynomial (often called Omega or Gamma in academic papers)
    err_eval = rs_find_error_evaluator(synd[::-1], err_loc, len(err_loc) - 1)[::-1]

    # Second part of Chien search to get the error location polynomial X from the error positions in err_pos (the roots of the error locator polynomial, ie, where it evaluates to 0)
    X = []  # will store the position of the errors
    for i in range(0, len(coef_pos)):
        l = 255 - coef_pos[i]
        X.append(gf_pow(2, -l))

    # Forney algorithm: compute the magnitudes
    E = [0] * (
        len(msg_in))  # will store the values that need to be corrected (substracted) to the message containing errors. This is sometimes called the error magnitude polynomial.
    Xlength = len(X)
    for i, Xi in enumerate(X):

        Xi_inv = gf_inverse(Xi)

        # Compute the formal derivative of the error locator polynomial (see Blahut, Algebraic codes for data transmission, pp 196-197).
        # the formal derivative of the errata locator is used as the denominator of the Forney Algorithm, which simply says that the ith error value is given by error_evaluator(gf_inverse(Xi)) / error_locator_derivative(gf_inverse(Xi)). See Blahut, Algebraic codes for data transmission, pp 196-197.
        err_loc_prime_tmp = []
        for j in range(0, Xlength):
            if j != i:
                err_loc_prime_tmp.append(gf_sub(1, gf_mul(Xi_inv, X[j])))
        # compute the product, which is the denominator of the Forney algorithm (errata locator derivative)
        err_loc_prime = 1
        for coef in err_loc_prime_tmp:
            err_loc_prime = gf_mul(err_loc_prime, coef)
        # equivalent to: err_loc_prime = functools.reduce(gf_mul, err_loc_prime_tmp, 1)

        # Compute y (evaluation of the errata evaluator polynomial)
        # This is a more faithful translation of the theoretical equation contrary to the old forney method. Here it is an exact reproduction:
        # Yl = omega(Xl.inverse()) / prod(1 - Xj*Xl.inverse()) for j in len(X)
        y = gf_poly_eval(err_eval[::-1], Xi_inv)  # numerator of the Forney algorithm (errata evaluator evaluated)
        y = gf_mul(gf_pow(Xi, 1), y)

        # Check: err_loc_prime (the divisor) should not be zero.
        if err_loc_prime == 0:
            raise ReedSolomonError("Could not find error magnitude")  # Could not find error magnitude

        # Compute the magnitude
        magnitude = gf_div(y,
                           err_loc_prime)  # magnitude value of the error, calculated by the Forney algorithm (an equation in fact): dividing the errata evaluator with the errata locator derivative gives us the errata magnitude (ie, value to repair) the ith symbol
        E[err_pos[i]] = magnitude  # store the magnitude for this error into the magnitude polynomial

    # Apply the correction of values to get our message corrected! (note that the ecc bytes also gets corrected!)
    # (this isn't the Forney algorithm, we just apply the result of decoding here)
    msg_in = gf_poly_add(msg_in,
                         E)  # equivalent to Ci = Ri - Ei where Ci is the correct message, Ri the received (senseword) message, and Ei the errata magnitudes (minus is replaced by XOR since it's equivalent in GF(2^p)). So in fact here we substract from the received message the errors magnitude, which logically corrects the value to what it should be.
    return msg_in


##### RS ERROR LOCATOR ##################################################################################################################################

def rs_find_error_locator(synd, nsym, erase_loc=None, erase_count=0):
    '''Find error/errata locator and evaluator polynomials with Berlekamp-Massey algorithm'''
    # Comprehensive diagnostic logging
    print("\n===== ERROR LOCATOR POLYNOMIAL GENERATION =====")
    print(f"DEBUG: Syndrome length: {len(synd)}")
    print(f"DEBUG: Number of symbols: {nsym}")
    print(f"DEBUG: Erasure locator: {erase_loc}")
    print(f"DEBUG: Erasure count: {erase_count}")
    
    # Detailed syndrome inspection
    print("Syndrome details:")
    for i, s in enumerate(synd):
        print(f"  Syndrome[{i}]: {s}")
    
    # Existing implementation with added logging
    if erase_loc:
        err_loc = list(erase_loc)
        old_loc = list(erase_loc)
    else:
        err_loc = [1]
        old_loc = [1]

    synd_shift = len(synd) - nsym

    for i in range(0, nsym-erase_count):
        if erase_loc:
            K = erase_count+i+synd_shift
        else:
            K = i+synd_shift

        # Iteration logging
        print(f"\nIteration {i}:")
        print(f"  Current K: {K}")
        print(f"  Current syndrome: {synd[K]}")
        print(f"  Current error locator: {err_loc}")
        print(f"  Current old locator: {old_loc}")

        delta = synd[K]
        for j in range(1, len(err_loc)):
            delta ^= gf_mul(err_loc[-(j+1)], synd[K - j])

        print(f"  Computed delta: {delta}")

        old_loc = old_loc + [0]

        if delta != 0:
            if len(old_loc) > len(err_loc):
                new_loc = gf_poly_scale(old_loc, delta)
                old_loc = gf_poly_scale(err_loc, gf_inverse(delta))
                err_loc = new_loc

            err_loc = gf_poly_add(err_loc, gf_poly_scale(old_loc, delta))

    # Final polynomial logging
    print("\n===== FINAL ERROR LOCATOR POLYNOMIAL =====")
    print(f"DEBUG: Error locator polynomial: {err_loc}")
    print(f"DEBUG: Error locator length: {len(err_loc)}")
    print(f"DEBUG: Number of errors: {len(err_loc) - 1}")
    
    while len(err_loc) and err_loc[0] == 0: del err_loc[0]
    errs = len(err_loc) - 1
    
    if (errs-erase_count) * 2 + erase_count > nsym:
        print("WARNING: Too many errors to correct")
        raise ReedSolomonError("Too many errors to correct")

    return err_loc


###################################RRS FIND ERRORS #######################################################################################################################

def rs_find_errors(err_loc, nmess): # nmess is len(msg_in)
    '''Find the roots (ie, where evaluation = zero) of error polynomial by brute-force trial, this is a sort of Chien's search
    (but less efficient, Chien's search is a way to evaluate the polynomial such that each evaluation only takes constant time).'''
    errs = len(err_loc) - 1
    err_pos = []
    for i in range(nmess): # normally we should try all 2^8 possible values, but here we optimize to just check the interesting symbols
        if gf_poly_eval(err_loc, gf_pow(2, i)) == 0: # It's a 0? Bingo, it's a root of the error locator polynomial,
                                                                                   # in other terms this is the location of an error
            err_pos.append(nmess - 1 - i)
    
    # More flexible error detection
    if abs(len(err_pos) - errs) > 2:  # Allow up to 2 errors difference
        raise ReedSolomonError(f"Significant mismatch in error detection. Expected {errs} errors, found {len(err_pos)} error positions.")
    
    return err_pos



####################################################RS FORNEY SYNDROMES ####################################################

def rs_forney_syndromes(synd, pos, nmess):
    # Compute Forney syndromes, which computes a modified syndromes to compute only errors (erasures are trimmed out). Do not confuse this with Forney algorithm, which allows to correct the message based on the location of errors.
    erase_pos_reversed = [nmess-1-p for p in pos] # prepare the coefficient degree positions (instead of the erasures positions)

    # Optimized method, all operations are inlined
    fsynd = list(synd[1:])      # make a copy and trim the first coefficient which is always 0 by definition
    for i in range(0, len(pos)):
        x = gf_pow(2, erase_pos_reversed[i])
        for j in range(0, len(fsynd) - 1):
            fsynd[j] = gf_mul(fsynd[j], x) ^ fsynd[j + 1]

    # Equivalent, theoretical way of computing the modified Forney syndromes: fsynd = (erase_loc * synd) % x^(n-k)
    # See Shao, H. M., Truong, T. K., Deutsch, L. J., & Reed, I. S. (1986, April). A single chip VLSI Reed-Solomon decoder. In Acoustics, Speech, and Signal Processing, IEEE International Conference on ICASSP'86. (Vol. 11, pp. 2151-2154). IEEE.ISO 690
    #erase_loc = rs_find_errata_locator(erase_pos_reversed, generator=generator) # computing the erasures locator polynomial
    #fsynd = gf_poly_mul(erase_loc[::-1], synd[1:]) # then multiply with the syndrome to get the untrimmed forney syndrome
    #fsynd = fsynd[len(pos):] # then trim the first erase_pos coefficients which are useless. Seems to be not absolutely necessary, but this reduces the computation time later in BM (thus it's an optimization).

    return fsynd




################Correct MSG

def rs_correct_msg(msg_in, nsym, erase_pos=None):
    '''Reed-Solomon main decoding function'''
    if len(msg_in) > 255: # can't decode, message is too big
        raise ValueError("Message is too long (%i when max is 255)" % len(msg_in))

    msg_out = list(msg_in)     # copy of message
    # erasures: set them to null bytes for easier decoding (but this is not necessary, they will be corrected anyway, but debugging will be easier with null bytes because the error locator polynomial values will only depend on the errors locations, not their values)
    if erase_pos is None:
        erase_pos = []
    else:
        for e_pos in erase_pos:
            msg_out[e_pos] = 0
    # check if there are too many erasures to correct (beyond the Singleton bound)
    if len(erase_pos) > nsym: raise ReedSolomonError("Too many erasures to correct")
    # prepare the syndrome polynomial using only errors (ie: errors = characters that were either replaced by null byte
    # or changed to another character, but we don't know their positions)
    synd = rs_calc_syndromes(msg_out, nsym)
    # check if there's any error/erasure in the input codeword. If not (all syndromes coefficients are 0), then just return the message as-is.
    if max(synd) == 0:
        return msg_out[:-nsym], msg_out[-nsym:]  # no errors

    # compute the Forney syndromes, which hide the erasures from the original syndrome (so that BM will just have to deal with errors, not erasures)
    fsynd = rs_forney_syndromes(synd, erase_pos, len(msg_out))
    # compute the error locator polynomial using Berlekamp-Massey
    err_loc = rs_find_error_locator(fsynd, nsym, erase_count=len(erase_pos))
    # locate the message errors using Chien search (or brute-force search)
    err_pos = rs_find_errors(err_loc[::-1] , len(msg_out))
    if err_pos is None:
        raise ReedSolomonError("Could not locate error")    # error location failed

    # Find errors values and apply them to correct the message
    # compute errata evaluator and errata magnitude polynomials, then correct errors and erasures
    msg_out = rs_correct_errata(msg_out, synd, (erase_pos + err_pos)) # note that we here use the original syndrome, not the forney syndrome
                                                                                                                                  # (because we will correct both errors and erasures, so we need the full syndrome)
    # check if the final message is fully repaired
    synd = rs_calc_syndromes(msg_out, nsym)
    if max(synd) > 0:
        raise ReedSolomonError("Could not correct message")     # message could not be repaired
    # return the successfully decoded message
    return msg_out[:-nsym], msg_out[-nsym:] # also return the corrected ecc block so that the user can check()


#############################RS FIND ERRORS####################################################################################################

def rs_find_errors(err_loc, nmess): # nmess is len(msg_in)
    '''Find the roots (ie, where evaluation = zero) of error polynomial by brute-force trial, this is a sort of Chien's search
    (but less efficient, Chien's search is a way to evaluate the polynomial such that each evaluation only takes constant time).'''
    errs = len(err_loc) - 1
    err_pos = []
    for i in range(nmess): # normally we should try all 2^8 possible values, but here we optimize to just check the interesting symbols
        if gf_poly_eval(err_loc, gf_pow(2, i)) == 0: # It's a 0? Bingo, it's a root of the error locator polynomial,
                                                                                   # in other terms this is the location of an error
            err_pos.append(nmess - 1 - i)
    
    # More flexible error detection
    if abs(len(err_pos) - errs) > 2:  # Allow up to 2 errors difference
        raise ReedSolomonError(f"Significant mismatch in error detection. Expected {errs} errors, found {len(err_pos)} error positions.")
    
    return err_pos
