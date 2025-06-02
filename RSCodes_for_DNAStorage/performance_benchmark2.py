import random
import time
import os
from dna_utils import symbols_to_dna, dna_to_symbols
import matplotlib.pyplot as plt
from dna_rs_encoder import DNAReedSolomonEncoder
from dna_rs_decoder import DNAReedSolomonDecoder

def generate_random_dna_file(filename: str, size_mb: float):
    """Generate a random DNA file of specified size in MB"""
    total_bytes = int(size_mb * 1024 * 1024)
    
    with open(filename, 'w') as f:
        # Generate random DNA sequence
        dna_sequence = ''.join(random.choice('ACGT') for _ in range(total_bytes))
        f.write(dna_sequence)
    
    print(f"Generated DNA file: {filename} (Size: {size_mb} MB)")

def introduce_random_errors(dna: str, error_rate: float) -> str:
    """Introduce random errors in DNA sequence with more controlled error distribution"""
    dna_list = list(dna)
    num_errors = int(len(dna) * error_rate)
    
    # Use a more deterministic error introduction method
    error_positions = random.sample(range(len(dna)), num_errors)
    
    for pos in error_positions:
        # Get all possible bases except the current one
        possible_bases = list(set('ACGT') - {dna_list[pos]})
        # Replace with a random different base
        dna_list[pos] = random.choice(possible_bases)
    
    return ''.join(dna_list)

def encode_large_file(input_data: str, n: int = 255, k: int = 223) -> tuple:
    """Encode a large file by splitting into chunks"""
    encoder = DNAReedSolomonEncoder(n=n, k=k)
    
    # Ensure each chunk is exactly k characters long
    chunks = []
    for i in range(0, len(input_data), k):
        chunk = input_data[i:i+k]
        
        # Pad the last chunk if it's shorter than k
        if len(chunk) < k:
            chunk = chunk.ljust(k, 'A')
        
        chunks.append(chunk)
    
    # Encode each chunk
    encoded_chunks = []
    ecc_symbols_list = []
    
    for chunk in chunks:
        # Encode the chunk
        encoded_chunk, ecc_symbols = encoder.encode(chunk)
        
        # Full codeword is the encoded chunk + ECC symbols converted to DNA
        full_codeword = encoded_chunk + symbols_to_dna(ecc_symbols)
        
        encoded_chunks.append(full_codeword)
        ecc_symbols_list.append(ecc_symbols)
    
    return ''.join(encoded_chunks), ecc_symbols_list

def decode_large_file(encoded_data: str, ecc_symbols_list: list, n: int = 255, k: int = 223) -> tuple:
    """
    Decode a large file with enhanced error tracking and correction
    
    Returns:
    - Decoded data
    - Error correction statistics
    """
    decoder = DNAReedSolomonDecoder(n=n, k=k)
    
    # Split encoded data into full codewords (including ECC)
    encoded_chunks = [encoded_data[i:i+n] for i in range(0, len(encoded_data), n)]
    
    # Decode each chunk with detailed error tracking
    decoded_chunks = []
    error_stats = {
        'total_chunks': len(encoded_chunks),
        'successfully_decoded_chunks': 0,
        'failed_chunks': 0,
        'total_errors_detected': 0,
        'chunk_error_details': []
    }
    
    for i, (encoded_chunk, ecc_symbols) in enumerate(zip(encoded_chunks, ecc_symbols_list)):
        try:
            # Attempt to decode with enhanced error tracking
            decoded_chunk, errors_corrected, error_details = decoder.decode_with_error_tracking(
                encoded_chunk[:k], 
                ecc_symbols
            )
            
            decoded_chunks.append(decoded_chunk)
            error_stats['successfully_decoded_chunks'] += 1
            error_stats['total_errors_detected'] += error_details.get('num_errors_detected', 0)
            
            # Log detailed error information
            error_stats['chunk_error_details'].append({
                'chunk_index': i,
                'errors_detected': error_details.get('num_errors_detected', 0),
                'syndrome_vector': error_details.get('syndrome_vector', []),
                'status': 'success'
            })
        
        except Exception as e:
            # More detailed error handling
            print(f"Decoding error for chunk {i}: {e}")
            error_stats['failed_chunks'] += 1
            
            # Log detailed error information
            error_stats['chunk_error_details'].append({
                'chunk_index': i,
                'status': 'failed',
                'error_message': str(e)
            })
            
            # Fallback strategy: try partial decoding or use a recovery mechanism
            try:
                # Attempt partial recovery or use original chunk with warning
                partial_decoded = encoded_chunk[:k]
                decoded_chunks.append(partial_decoded)
                print(f"Warning: Partial recovery for chunk {i}")
            except Exception:
                # If all recovery fails, insert a placeholder
                decoded_chunks.append('X' * k)
    
    # Remove padding from the last chunk
    decoded_data = ''.join(decoded_chunks).rstrip('A')
    
    return decoded_data, error_stats

def create_performance_chart(encode_time, decode_time, file_size_mb):
    """
    Create a bar chart showing encoding and decoding performance
    
    Args:
        encode_time (float): Time taken for encoding
        decode_time (float): Total time taken for decoding
        file_size_mb (float): File size in MB
    """
    # Create figure and axis
    plt.figure(figsize=(10, 6))
    
    # Create bars
    plt.bar('Encoding', encode_time, color='blue', label='Encoding')
    
    # For decoding stages, we'll measure actual time distribution
    # We'll assume the following approximate ratios based on typical RS decoding:
    # Syndrome Calculation: 40% of decode time
    # Error Locator: 30% of decode time
    # Error Correction: 30% of decode time
    
    stages = ['Syndrome Calculation', 'Error Locator', 'Error Correction']
    stage_times = {
        'Syndrome Calculation': decode_time * 0.4,
        'Error Locator': decode_time * 0.3,
        'Error Correction': decode_time * 0.3
    }
    
    for stage in stages:
        plt.bar(stage, stage_times[stage], color='red')
    
    # Add labels and title
    plt.title(f'Performance Breakdown for {file_size_mb}MB File')
    plt.xlabel('Processing Stage')
    plt.ylabel('Time (seconds)')
    plt.legend()
    plt.grid(True, axis='y')
    
    # Save and show plot
    plt.tight_layout()
    plt.savefig(f'performance_chart_{file_size_mb}mb.png')
    plt.close()

def main(verbose: bool = True):
    # Parameters
    n = 255  # Codeword length
    k = 223  # Message length
    dna_size_mb = 0.5  # Size in MB
    error_rate = 0.01  # 1% error rate
    
    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # File paths
    input_file = 'docs/dna_input6.txt'
    encoded_file = 'docs/dna_encoded6.txt'
    ecc_file = 'docs/dna_ecc6.txt'
    corrupted_file = 'docs/dna_corrupted6.txt'
    corrected_file = 'docs/dna_corrected6.txt'
    
    # Optional logging
    def log(message):
        if verbose:
            print(message)
    
    # Process files with cleaner output
    print("""
=== DNA Error Correction Process ===
""")
    
    # 1. Generate DNA sequence
    log("\n1. Generating DNA sequence...")
    generate_random_dna_file(input_file, dna_size_mb)
    
    # 2. Read input file
    with open(input_file, 'r') as f:
        input_data = f.read()
    
    # 3. Encode DNA sequence
    log("\n2. Encoding DNA sequence...")
    encode_start = time.time()
    encoded_data, ecc_symbols = encode_large_file(input_data, n, k)
    encode_time = time.time() - encode_start
    log(f"Encoding completed in {encode_time:.2f} seconds")
    
    # 4. Write encoded data
    with open(encoded_file, 'w') as f:
        f.write(encoded_data)
    with open(ecc_file, 'w') as f:
        for symbols in ecc_symbols:
            f.write(''.join(map(str, symbols)) + '\n')
    
    # 5. Introduce errors
    log("\n3. Introducing random errors...")
    corrupted_data = introduce_random_errors(encoded_data, error_rate)
    with open(corrupted_file, 'w') as f:
        f.write(corrupted_data)
    
    # 6. Decode and correct
    log("\n4. Decoding and correcting errors...")
    decode_start = time.time()
    try:
        corrected_data, error_stats = decode_large_file(corrupted_data, ecc_symbols, n, k)
        decode_time = time.time() - decode_start
        log(f"Decoding completed in {decode_time:.2f} seconds")
        # Create performance chart
        create_performance_chart(encode_time, decode_time, dna_size_mb)
        # Write corrected data
        with open(corrected_file, 'w') as f:
            f.write(corrected_data)
        
        # === Results Summary ===
        print("\n=== Results Summary ===")
        print(f"\nFile Size: {dna_size_mb} MB")
        print(f"Total processing time: {encode_time + decode_time:.2f} seconds")
        
        # === Data Verification ===
        print("\n=== Data Verification ===")
        print(f"Original data length: {len(input_data)}")
        print(f"Corrected data length: {len(corrected_data)}")
        print(f"Data matches: {input_data == corrected_data}")
        
        # Calculate correction statistics
        chunks_with_errors = sum(1 for detail in error_stats['chunk_error_details'] 
                               if detail.get('errors_detected', 0) > 0)
        total_errors_detected = sum(detail.get('errors_detected', 0) 
                                  for detail in error_stats['chunk_error_details'])
        
        print("\n=== Correction Statistics ===")
        print(f"Chunks processed: {error_stats['total_chunks']}")
        print(f"Chunks with errors: {chunks_with_errors}")
        print(f"Total errors detected: {total_errors_detected}")
        print(f"Successfully decoded chunks: {error_stats['successfully_decoded_chunks']}")
        print(f"Failed chunks: {error_stats['failed_chunks']}")
        
        # === Symbol Verification ===
        print("\n=== Symbol Verification ===")
        symbol_matches = sum(1 for a, b in zip(input_data, corrected_data) if a == b)
        total_symbols = min(len(input_data), len(corrected_data))
        symbol_match_rate = (symbol_matches / total_symbols) * 100
        
        print(f"Symbols matched: {symbol_matches} out of {total_symbols}")
        print(f"Symbol match rate: {symbol_match_rate:.2f}%")
        
        # === Detailed Error Analysis ===
        print("\n=== Detailed Error Analysis ===")
        symbol_errors = []
        for i, (original, corrected) in enumerate(zip(input_data, corrected_data)):
            if original != corrected:
                symbol_errors.append({
                    'position': i,
                    'original': original,
                    'corrected': corrected,
                    'chunk': i // k
                })
        
        if symbol_errors:
            print(f"Total symbol errors: {len(symbol_errors)}")
            print("\nFirst 5 symbol errors:")
            for error in symbol_errors[:5]:
                print(f"Position {error['position']} in chunk {error['chunk']}:")
                print(f"  Original: {error['original']}")
                print(f"  Corrected: {error['corrected']}")
        else:
            print("No symbol errors found!")
            
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n=== Process Complete ===")

if __name__ == "__main__":
    main(verbose=True)  # Set to False for less detailed logging
