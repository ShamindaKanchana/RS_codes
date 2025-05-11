from init_tables import init_tables
from encode import rs_encode_msg
from decode import rs_correct_msg
from gf_operations import set_gf_tables

# Configuration of the parameters and input message
prim = 0x11d
n = 20 # set the size you want, it must be > k, the remaining n-k symbols will be the ECC code (more is better)
k = 11 # k = len(message)
message = "My name is Shaminda" # input message

# Initializing the log/antilog tables and setting them globally
gf_exp, gf_log = init_tables(prim)
set_gf_tables(gf_exp, gf_log)

# Encoding the input message
mesecc = rs_encode_msg([ord(x) for x in message], n-k)
print("Original: %s" % mesecc)

# Tampering 6 characters of the message (over 9 ecc symbols, so we are above the Singleton Bound)
mesecc[0] = 0
mesecc[1] = 2
mesecc[2] = 2
mesecc[3] = 2
mesecc[4] = 2
mesecc[5] = 2
print("Corrupted: %s" % mesecc)

# Decoding/repairing the corrupted message, by providing the locations of a few erasures, we get below the Singleton Bound
# Remember that the Singleton Bound is: 2*e+v <= (n-k)
corrected_message, corrected_ecc = rs_correct_msg(mesecc, n-k, erase_pos=[0, 1, 2])
print("Repaired: %s" % (corrected_message+corrected_ecc))
print(''.join([chr(x) for x in corrected_message]))