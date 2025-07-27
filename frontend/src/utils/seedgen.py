#!/usr/bin/env python3
import hashlib
import hmac
import argparse
import re
import secrets
import time
import sys
import os
from typing import List, Optional

def clean_input(text: str) -> str:
    """Clean user input by normalizing whitespace"""
    return re.sub(r'\s+', ' ', text).strip()

def method_1_entropy_mixing(words: str, salt: str = "", detail: bool = False) -> str:
    """
    Method 1: Entropy Mixing
    Mixes the entropy from all input words with custom salt using
    multiple hash functions and iterations.
    """
    print("\n[Method 1: Entropy Mixing]")
    print("Mixing entropy from all words with advanced hashing...")
    
    # Start with the basic input
    result = words.encode('utf-8')
    input_bytes = len(result)
    
    # Add salt if provided
    if salt:
        result = result + salt.encode('utf-8')
        if detail:
            print(f"  Added salt to entropy source ({len(salt)} characters)")
    
    if detail:
        print(f"\n  🔍 INPUT DETAILS:")
        print(f"  • Source text: {len(words)} characters")
        print(f"  • Input bytes: {input_bytes} bytes")
        print(f"  • Hash rounds: 1000 iterations")
        print(f"  • Algorithms : SHA-512, SHA3-512, BLAKE2b (rotating)")
        
        # Show initial state partial hash
        initial_hash = hashlib.sha256(result).hexdigest()[:16]
        print(f"  • Initial state (partial): {initial_hash}...")
        print("\n  🔄 PROCESSING ROUNDS:")
    
    # Perform multiple rounds of hashing with different algorithms
    milestones = [100, 250, 500, 750, 900, 999] if detail else []
    
    for i in range(1000):
        if i % 3 == 0:
            algo = "SHA-512"
            result = hashlib.sha512(result).digest()
        elif i % 3 == 1:
            algo = "SHA3-512"
            result = hashlib.sha3_512(result).digest()
        else:
            algo = "BLAKE2b"
            result = hashlib.blake2b(result, digest_size=64).digest()
            
        # Add some iteration-specific data to prevent cycles
        result += str(i).encode('utf-8')
        
        # Show milestone details if requested
        if detail and i in milestones:
            current = result[:4].hex()
            print(f"  • Round {i+1:4d}: Using {algo:8s} → {current}...")
    
    # Final hash to get our 64-character output
    final_hash = hashlib.sha512(result).hexdigest()[:64]
    
    if detail:
        print("\n  🏁 FINAL PROCESSING:")
        print(f"  • Applied final SHA-512 hash")
        print(f"  • Extracted first 64 hex characters")
    
    print(f"\n✅ Entropy successfully mixed using 1000 rounds of multi-algorithm hashing")
    return final_hash

def method_2_personal_mixer(words: str, personal_info: str = "", detail: bool = False) -> str:
    """
    Method 2: Personal Mixer
    Uses personal information mixed with words to create a seed that
    combines multiple personal factors with the input.
    """
    print("\n[Method 2: Personal Mixer]")
    print("Creating personalized seed from words and personal information...")
    
    # Normalize inputs
    normalized_words = words.lower()
    
    # Create a base from words
    base = normalized_words.encode('utf-8')
    
    # Add personal info if provided
    system_entropy = False
    if personal_info:
        print(f"Adding personal information to increase uniqueness")
        base += personal_info.encode('utf-8')
    else:
        print(f"No personal information provided, using system data for additional entropy")
        system_entropy = True
        # Add some system-specific data for additional entropy
        pid = os.getpid()
        timestamp = time.time_ns()
        base += str(pid).encode('utf-8')
        base += str(timestamp).encode('utf-8')
    
    if detail:
        print(f"\n  🔍 INPUT DETAILS:")
        print(f"  • Word source: {len(normalized_words)} characters")
        if personal_info:
            print(f"  • Personal info: {len(personal_info)} characters")
        if system_entropy:
            print(f"  • System entropy: Process ID and timestamp added")
        print(f"  • HMAC rounds: 2048 iterations with SHA3-512")
        print(f"  • Key updates: Modified on each iteration")
        
        # Show initial state
        initial_hash = hashlib.sha256(base).hexdigest()[:16]
        print(f"  • Initial state (partial): {initial_hash}...")
        print("\n  🔄 PROCESSING ROUNDS:")
    
    # Create a unique key from the base data
    key = hashlib.sha3_256(base).digest()
    
    # Use HMAC with multiple iterations
    result = base
    milestones = [0, 512, 1024, 1536, 2047] if detail else []
    
    for i in range(2048):
        result = hmac.new(key, result, hashlib.sha3_512).digest()
        # Modify the key slightly each time
        key = hashlib.sha3_256(key + bytes([i & 0xFF])).digest()
        
        # Show milestone details if requested
        if detail and i in milestones:
            current = result[:4].hex()
            key_sample = key[:2].hex()
            print(f"  • Round {i+1:4d}: HMAC-SHA3-512 → {current}... (key: {key_sample}...)")
    
    # Get final 64-character hex
    final_hash = result.hex()[:64]
    
    if detail:
        print("\n  🏁 FINAL PROCESSING:")
        print(f"  • Converted final HMAC result to hex")
        print(f"  • Extracted first 64 hex characters")
    
    print(f"\n✅ Personal seed created with 2048 rounds of keyed hashing")
    return final_hash

def method_3_diceware_style(words: str, detail: bool = False) -> str:
    """
    Method 3: Diceware-Style Mixing
    Treats each word as a diceware-style element and mixes them in a
    deterministic but highly complex pattern.
    """
    print("\n[Method 3: Word Pattern Mixing]")
    print("Creating seed using word pattern analysis...")
    
    # Split words and ensure we have enough data
    word_list = words.split()
    
    if len(word_list) < 3:
        print("Warning: For best results, provide at least 3 words")
        # Pad with repeated words if needed
        while len(word_list) < 3:
            word_list.append(word_list[0] if word_list else "entropy")
    
    if detail:
        print(f"\n  🔍 INPUT DETAILS:")
        print(f"  • Word count: {len(word_list)} words")
        print(f"  • Total characters: {len(words)} characters")
        
        # Show words with their lengths if not too many
        if len(word_list) <= 12:
            word_details = [f"{word} ({len(word)})" for word in word_list]
            print(f"  • Words: {', '.join(word_details)}")
        else:
            print(f"  • First 5 words: {', '.join(word_list[:5])}, ...")
            
        print(f"  • Pattern mixing: Each word affects all 64 bytes")
        print("\n  🔄 WORD HASHING:")
    
    # Create initial bytes from words
    word_bytes = []
    for i, word in enumerate(word_list):
        # Get consistent bytes for each word
        word_hash = hashlib.sha256(word.encode('utf-8')).digest()
        word_bytes.append(word_hash)
        
        if detail and i < 5:  # Show first 5 words only to avoid clutter
            hash_sample = word_hash[:4].hex()
            print(f"  • Word {i+1:2d} '{word}': SHA-256 → {hash_sample}...")
    
    # Mix the bytes in a complex pattern
    print(f"\nMixing {len(word_list)} words with pattern-based algorithm...")
    mixed = bytearray(64)
    
    if detail:
        print("\n  🔄 BYTE MIXING PATTERN:")
        pattern_samples = [8, 16, 32, 48, 63]  # Sample positions to show
    
    # Fill the mixed array using a pattern based on the words
    for i in range(64):
        byte_value = i
        for j, word_hash in enumerate(word_bytes):
            # Use different portions of each word hash based on position
            index = (i + j) % len(word_hash)
            # XOR the bytes in a rotating pattern
            byte_value ^= word_hash[index]
            # Add some position-dependent mixing
            byte_value = (byte_value + word_hash[(index * 3 + j) % len(word_hash)]) % 256
        
        mixed[i] = byte_value
        
        if detail and i in pattern_samples:
            print(f"  • Byte {i:2d}: Mixed {len(word_list)} words → {byte_value:02x}")
    
    # Final processing with SHA3
    result = hashlib.sha3_512(mixed).hexdigest()[:64]
    
    if detail:
        print("\n  🏁 FINAL PROCESSING:")
        print(f"  • Applied SHA3-512 to mixed byte array")
        print(f"  • Extracted first 64 hex characters")
    
    print(f"\n✅ Word pattern mixing complete with {len(word_list)} input patterns")
    return result

def generate_seed_from_words(words: str, method: int = 1, salt: str = "", personal_info: str = "", detail: bool = False) -> str:
    """Generate a 64-character hex seed from words using the specified method"""
    
    if method == 1:
        return method_1_entropy_mixing(words, salt, detail)
    elif method == 2:
        return method_2_personal_mixer(words, personal_info, detail)
    elif method == 3:
        return method_3_diceware_style(words, detail)
    else:
        raise ValueError(f"Invalid method: {method}. Choose 1, 2, or 3.")

def generate_random_words(count: int, detail: bool = False) -> str:
    """Generate random words as seed input for users who want completely random input"""
    # Simple word list for random generation
    simple_words = [
        "apple", "banana", "orange", "grape", "kiwi", "melon", "peach", "plum",
        "dog", "cat", "bird", "fish", "lion", "tiger", "bear", "wolf", "fox",
        "red", "blue", "green", "yellow", "black", "white", "purple", "orange",
        "big", "small", "fast", "slow", "hot", "cold", "old", "new", "good", "bad",
        "happy", "sad", "angry", "calm", "loud", "quiet", "rich", "poor",
        "sun", "moon", "star", "cloud", "rain", "snow", "wind", "storm",
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
    ]
    
    if detail:
        print(f"\n  🎲 RANDOM WORD SELECTION:")
        print(f"  • Selecting from a pool of {len(simple_words)} common words")
        print(f"  • Generating {count} random words")
        print(f"  • Using Python's secrets module for cryptographic randomness")
    
    # Select random words
    result = []
    for i in range(count):
        word_index = secrets.randbelow(len(simple_words))
        word = simple_words[word_index]
        result.append(word)
        
        if detail:
            if i < 5 or i > count - 3:  # Show first 5 and last 2 selections
                print(f"  • Word {i+1:2d}: Selected '{word}' (index: {word_index})")
            elif i == 5 and count > 10:
                print(f"  • ... {count - 7} more words ...")
    
    return " ".join(result)

def main():
    parser = argparse.ArgumentParser(
        description="Generate a 64-character hex seed from any words using different methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seedgen.py --words "my custom phrase with any words"
  python seedgen.py --words "personal secret" --method 2 --personal "born:1990,city:NewYork"
  python seedgen.py --words "completely random words" --method 3
  python seedgen.py --random 15 --method 1
  python seedgen.py --words "show me details" --method 1 --detail
        """
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--words", type=str, help="Custom words to convert to seed (can be any text)")
    group.add_argument("--random", type=int, help="Generate random word sequence with specified number of words")
    
    parser.add_argument("--method", type=int, choices=[1, 2, 3], default=1,
                        help="Seed generation method: 1=Entropy Mixing, 2=Personal Mixer, 3=Word Pattern Mixing")
    parser.add_argument("--salt", type=str, default="", help="Optional salt for Method 1")
    parser.add_argument("--personal", type=str, default="", help="Personal information for Method 2")
    parser.add_argument("--output", type=str, help="Output file to save the seed (optional)")
    parser.add_argument("--detail", "-d", action="store_true", help="Show detailed information about the seed generation process")
    
    args = parser.parse_args()
    
    # Get input words
    if args.random:
        words = generate_random_words(args.random, args.detail)
        print(f"Generated {args.random} random words as input:")
        print(f"  {words}")
    else:
        words = clean_input(args.words)
        print(f"Using custom input: \"{words}\"")
    
    # Generate seed using the selected method
    try:
        seed_hex = generate_seed_from_words(
            words, 
            method=args.method,
            salt=args.salt,
            personal_info=args.personal,
            detail=args.detail
        )
        
        print("\n" + "=" * 60)
        print("FINAL SEED (64-character hex):")
        print(seed_hex)
        print("=" * 60)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(seed_hex)
            print(f"\nSeed saved to {args.output}")
        
        print("\n📋 Copy this seed into the 'Enter your seed directly' field in FiZk")
        print("🔒 IMPORTANT: Keep this seed secure! Anyone with it can access your account.")
        
    except Exception as e:
        print(f"\nError generating seed: {str(e)}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())