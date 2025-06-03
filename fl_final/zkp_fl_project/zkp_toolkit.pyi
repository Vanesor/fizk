"""
Type stubs for zkp_toolkit module.
This file helps IDEs understand the available methods in the zkp_toolkit module.
"""

def generate_schnorr_keys_ffi() -> tuple[str, str]:
    """Generate Schnorr key pair.
    
    Returns:
        Tuple of (secret_key_hex, public_key_hex)
    """
    ...

def generate_schnorr_proof_ffi(sk_hex: str, pk_hex: str, challenge_hex: str) -> bytes:
    """Generate Schnorr proof for authentication.
    
    Args:
        sk_hex: Secret key in hex format
        pk_hex: Public key in hex format  
        challenge_hex: Challenge string in hex format
        
    Returns:
        Schnorr proof as bytes
    """
    ...

def verify_schnorr_proof_ffi(pk_hex: str, proof: bytes, challenge_hex: str) -> bool:
    """Verify Schnorr proof.
    
    Args:
        pk_hex: Public key in hex format
        proof: Proof bytes
        challenge_hex: Challenge string in hex format
        
    Returns:
        True if proof is valid, False otherwise
    """
    ...

def generate_protostar_proof_ffi(computation_data: str) -> bytes:
    """Generate Protostar proof for computation.
    
    Args:
        computation_data: String representing the computation to prove
        
    Returns:
        Protostar proof as bytes
    """
    ...

def verify_and_aggregate_protogalaxy_ffi(proofs: list[bytes]) -> bytes:
    """Verify and aggregate multiple Protostar proofs using ProtoGalaxy.
    
    Args:
        proofs: List of Protostar proof bytes
        
    Returns:
        Aggregated proof as bytes
        
    Raises:
        ValueError: If any proof is invalid or aggregation fails
    """
    ...
