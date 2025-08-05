"""
Benchmarking DNA RS(15,11) encoding/decoding for 11-base sequences
"""
import time
from dna_rs_encoder import DNAReedSolomonEncoder
from dna_rs_decoder import DNAReedSolomonDecoder

def run_benchmark():
    # Test with 11-base sequence (matching RS(15,11) k=11)
    dna_sequence = "ACGTACGTACG"  # 11 bases
    print(f"Testing with sequence: {dna_sequence} (length: {len(dna_sequence)} bases)")
    
    # Initialize with RS(15,11) parameters
    n, k = 15, 11
    encoder = DNAReedSolomonEncoder(n=n, k=k)
    decoder = DNAReedSolomonDecoder(n=n, k=k)
    
    # Time encoding
    start_time = time.perf_counter()
    encoded_dna, ecc_symbols = encoder.encode(dna_sequence)
    encode_time = (time.perf_counter() - start_time) * 1e6  # microseconds
    
    # Corrupt the sequence (introduce 2 errors)
    corrupted_dna = list(encoded_dna)
    corrupted_dna[1] = 'C'  # 1st error
    corrupted_dna[5] = 'G'  # 2nd error
    corrupted_dna = ''.join(corrupted_dna)
    
    # Time decoding and error correction
    start_time = time.perf_counter()
    corrected_dna = decoder.decode(corrupted_dna, ecc_symbols)
    decode_time = (time.perf_counter() - start_time) * 1e6  # microseconds
    
    # Verify correction
    success = (corrected_dna == encoded_dna)
    
    print("\n--- Performance Results ---")
    print(f"Original:   {dna_sequence}")
    print(f"Encoded:    {encoded_dna}")
    print(f"Corrupted:  {corrupted_dna}")
    print(f"Corrected:  {corrected_dna}")
    print(f"\nEncoding time:   {encode_time:.2f} μs")
    print(f"Decoding time:   {decode_time:.2f} μs")
    print(f"Total time:      {(encode_time + decode_time):.2f} μs")
    print(f"Correction:      {'✅ SUCCESS' if success else '❌ FAILED'}")

def main():
    # Run multiple iterations for more accurate timing
    num_runs = 1000
    print(f"Running benchmark with {num_runs} iterations...")
    
    total_encode = 0
    total_decode = 0
    
    for i in range(num_runs):
        # Test with 11-base sequence (matching RS(15,11) k=11)
        dna_sequence = "ACGTACGTACG"  # 11 bases
        
        # Initialize with RS(15,11) parameters
        n, k = 15, 11
        encoder = DNAReedSolomonEncoder(n=n, k=k)
        decoder = DNAReedSolomonDecoder(n=n, k=k)
        
        # Time encoding
        start_time = time.perf_counter()
        encoded_dna, ecc_symbols = encoder.encode(dna_sequence)
        total_encode += (time.perf_counter() - start_time) * 1e6  # microseconds
        
        # Corrupt the sequence (introduce 2 errors)
        corrupted_dna = list(encoded_dna)
        corrupted_dna[1] = 'C'  # 1st error
        corrupted_dna[5] = 'G'  # 2nd error
        corrupted_dna = ''.join(corrupted_dna)
        
        # Time decoding and error correction
        start_time = time.perf_counter()
        corrected_dna = decoder.decode(corrupted_dna, ecc_symbols)
        total_decode += (time.perf_counter() - start_time) * 1e6  # microseconds
    
    print("\n--- Average Performance (1000 runs) ---")
    print(f"Average encode time: {total_encode/num_runs:.2f} μs")
    print(f"Average decode time: {total_decode/num_runs:.2f} μs")
    print(f"Total average time:  {(total_encode + total_decode)/num_runs:.2f} μs")

if __name__ == "__main__":
    # Run single test with output
    run_benchmark()
    
    # Run performance benchmark (averaged over many runs)
    main()
