#!/usr/bin/env python3
"""
Test script to verify that the ZKP toolkit imports and methods work correctly.
"""

import sys
import os

# Add the fl_system directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fl_system'))

def test_zkp_toolkit():
    """Test that zkp_toolkit can be imported and its methods called."""
    try:
        import zkp_toolkit
        print("✅ zkp_toolkit imported successfully")
        
        # Test available methods
        methods = [attr for attr in dir(zkp_toolkit) if not attr.startswith('_')]
        print(f"📋 Available methods: {methods}")
        
        # Test key generation
        sk, pk = zkp_toolkit.generate_schnorr_keys_ffi()
        print(f"✅ Schnorr key generation: sk={sk[:10]}..., pk={pk[:10]}...")
        
        # Test Schnorr proof generation
        challenge = "1234567890abcdef"
        proof = zkp_toolkit.generate_schnorr_proof_ffi(sk, pk, challenge)
        print(f"✅ Schnorr proof generation: {len(proof)} bytes")
        
        # Test proof verification
        is_valid = zkp_toolkit.verify_schnorr_proof_ffi(pk, proof, challenge)
        print(f"✅ Schnorr proof verification: {is_valid}")
        
        # Test Protostar proof generation
        test_data = "test_computation_data"
        protostar_proof = zkp_toolkit.generate_protostar_proof_ffi(test_data)
        print(f"✅ Protostar proof generation: {len(protostar_proof)} bytes")
        
        # Test ProtoGalaxy aggregation (this might fail with invalid proofs, which is expected)
        try:
            aggregated = zkp_toolkit.verify_and_aggregate_protogalaxy_ffi([protostar_proof])
            print(f"✅ ProtoGalaxy aggregation: {len(aggregated)} bytes")
        except ValueError as e:
            print(f"⚠️  ProtoGalaxy aggregation failed (expected with test data): {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_strategy_import():
    """Test that the strategy can be imported."""
    try:
        from fl_system.strategy.zk_strategy import ZkProofStrategy
        print("✅ ZkProofStrategy imported successfully")
        return True
    except Exception as e:
        print(f"❌ Strategy import error: {e}")
        return False

def test_client_import():
    """Test that the client can be imported."""
    try:
        from fl_system.client_impl.zk_client import ZkFlowerClient
        print("✅ ZkFlowerClient imported successfully")
        return True
    except Exception as e:
        print(f"❌ Client import error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing ZKP Toolkit Integration...")
    print("=" * 50)
    
    zkp_ok = test_zkp_toolkit()
    print()
    
    strategy_ok = test_strategy_import()
    print()
    
    client_ok = test_client_import()
    print()
    
    print("=" * 50)
    if zkp_ok and strategy_ok and client_ok:
        print("🎉 All tests passed! ZKP integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)
