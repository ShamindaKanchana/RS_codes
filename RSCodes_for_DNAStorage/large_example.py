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
    original_dna = ''.join(random.choices(bases, k=1000000))  # 500000 bases
    # decoding process have used 3 errors per chunk
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
        
        # Simulate errors in the encoded chunk, but stay within error correction capability
        # The RS code can correct up to (n-k)/2 errors per chunk
        max_errors = (n - k) // 2
        num_errors = min(3, max_errors)  # Introduce at most 3 errors or the max correctable
        
        corrupted_chunk = list(encoded_chunk)
        if num_errors > 0:
            # Ensure we don't try to sample more errors than positions available
            num_possible_errors = min(num_errors, len(encoded_chunk))
            if num_possible_errors > 0:
                error_positions = random.sample(range(len(encoded_chunk)), num_possible_errors)
                for pos in error_positions:
                    current_base = corrupted_chunk[pos]
                    possible_bases = list(set(bases) - {current_base})
                    corrupted_chunk[pos] = random.choice(possible_bases)
        corrupted_chunk = ''.join(corrupted_chunk)
        
        print(f"Introduced {num_errors} error(s) in positions: {error_positions if 'error_positions' in locals() else 'None'}")
        
        print(f"Corrupted chunk: {corrupted_chunk}")
        
        # Decode and correct errors
        try:
            corrected_chunk = decoder.decode(corrupted_chunk, ecc_symbols)
            corrected_chunks.append(corrected_chunk)
            
            print(f"Corrupted chunk: {corrupted_chunk}")
            print(f"Corrected chunk: {corrected_chunk}")
            
            # Verify correction
            if corrected_chunk == chunk:
                print("✓ Correction successful")
            else:
                print("✗ Correction failed")
                # Print the differences
                print("Mismatches:")
                for i, (orig, corr) in enumerate(zip(chunk, corrected_chunk)):
                    if orig != corr:
                        print(f"  Position {i}: Original={orig}, Corrected={corr}")
                        
        except Exception as e:
            print(f"Error during decoding: {str(e)}")
            # If decoding fails, use the original chunk to continue
            corrected_chunks.append(chunk)
            print("✗ Decoding failed, using original chunk")
            
    
    # Combine all corrected chunks back into a single sequence
    final_corrected_dna = ''.join(corrected_chunks)
    
    # Trim any padding from the last chunk
    final_corrected_dna = final_corrected_dna[:len(original_dna)]
    
    print("\nFinal Results:")
    print(f"Original DNA length: {len(original_dna)}")
    print(f"Final corrected DNA length: {len(final_corrected_dna)}")
    
    # Verify the entire sequence
    is_correct = final_corrected_dna == original_dna
    print(f"Overall correction successful: {is_correct}")
    
    if not is_correct:
        # Find and print the first few mismatches
        print("\nFirst few mismatches:")
        mismatch_count = 0
        for i, (orig, corr) in enumerate(zip(original_dna, final_corrected_dna)):
            if orig != corr and mismatch_count < 5:  # Show first 5 mismatches
                print(f"Position {i}: Original={orig}, Corrected={corr}")
                mismatch_count += 1
    
    # Save results to files
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    original_file = os.path.join(output_dir, 'original_dna.txt')
    corrected_file = os.path.join(output_dir, 'corrected_dna.txt')
    
    with open(original_file, 'w') as f:
        f.write(original_dna)
    with open(corrected_file, 'w') as f:
        f.write(final_corrected_dna)
        
    print(f"\nResults saved to {os.path.abspath(original_file)} and {os.path.abspath(corrected_file)}")



if __name__ == "__main__":
    main()
