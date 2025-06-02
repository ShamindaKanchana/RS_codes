"""
Example usage of DNA-specific Reed-Solomon error correction
"""
from dna_rs_encoder import DNAReedSolomonEncoder
from dna_rs_decoder import DNAReedSolomonDecoder
import random 
def main():
    # Create output directory if it doesn't exist
    import os
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    # Large DNA sequence parameters
    n = 30  # Total codeword length (20 data + 10 ECC)
    k = 20  # Message length (20 bases per chunk)
    chunk_size = k  # Each chunk will be 20 bases
    
    # Initialize encoder and decoder
    encoder = DNAReedSolomonEncoder(n=n, k=k)
    decoder = DNAReedSolomonDecoder(n=n, k=k)
    
    # Generate a large DNA sequence (for example)
    bases = ['A', 'C', 'G', 'T']
    original_dna = ''.join(random.choices(bases, k=10000))  # 1000 bases
    
    print(f"Original DNA sequence length: {len(original_dna)}")
    
    # Split into chunks
    chunks = [original_dna[i:i+chunk_size] for i in range(0, len(original_dna), chunk_size)]
    print(f"Number of chunks: {len(chunks)}")
    
    # Process each chunk independently
    encoded_chunks = []
    ecc_symbols_list = []
    corrected_chunks = []
    
    print("\nEncoding each chunk:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}/{len(chunks)}:")
        print(f"Original chunk: {chunk}")
        
        # Encode the chunk
        encoded_chunk, ecc_symbols = encoder.encode(chunk)
        encoded_chunks.append(encoded_chunk)
        ecc_symbols_list.append(ecc_symbols)
        
        print(f"Encoded chunk: {encoded_chunk}")
        print(f"ECC symbols: {ecc_symbols}")
        
        # Simulate errors in the encoded chunk
        corrupted_chunk = list(encoded_chunk)
        # Introduce random errors (up to 5 errors per chunk)
        error_positions = random.sample(range(len(encoded_chunk)), min(5, len(encoded_chunk)))
        for pos in error_positions:
            current_base = corrupted_chunk[pos]
            possible_bases = list(set(bases) - {current_base})
            corrupted_chunk[pos] = random.choice(possible_bases)
        corrupted_chunk = ''.join(corrupted_chunk)
        
        print(f"Corrupted chunk: {corrupted_chunk}")
        
        # Decode and correct errors with file output enabled
        corrected_chunk, num_errors, error_details, file_paths = decoder.decode_with_error_tracking(
            ''.join(corrupted_chunk), 
            ecc_symbols,
            save_to_files=True  # Enable file output
        )
        corrected_chunks.append(corrected_chunk)
        
        print(f"Corrupted chunk: {''.join(corrupted_chunk)}")
        print(f"Corrected chunk: {corrected_chunk}")
        print(f"Number of errors corrected: {num_errors}")
        print(f"Output files saved to: {file_paths}")
        
        # Verify correction
        if corrected_chunk == chunk:
            print("✓ Correction successful")
        else:
            print("✗ Correction failed")
            
    
    # Combine all corrected chunks back into a single sequence
    final_corrected_dna = ''.join([decoder.decode(c, ecc) for c, ecc in zip(encoded_chunks, ecc_symbols_list)])
    
    print("\nFinal Results:")
    print(f"Original DNA length: {len(original_dna)}")
    print(f"Final corrected DNA length: {len(final_corrected_dna)}")
    print(f"Overall correction successful: {final_corrected_dna == original_dna}")
    
    # Save results to files
    with open('original_dna.txt', 'w') as f:
        f.write(original_dna)
    with open('corrected_dna.txt', 'w') as f:
        f.write(final_corrected_dna)



if __name__ == "__main__":
    main()
