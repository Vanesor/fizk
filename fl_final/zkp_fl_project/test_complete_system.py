#!/usr/bin/env python3
"""
Complete System Test for Federated Learning with ZKP Integration
Tests the full workflow: ZKP toolkit, data loading, client creation, and strategy initialization
"""

import sys
import os
import numpy as np
from typing import Dict
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
fl_system_path = os.path.join(project_root, 'fl_system')
sys.path.append(project_root)
sys.path.append(fl_system_path)

def test_zkp_toolkit():
    """Test ZKP toolkit functionality"""
    print("🧪 Testing ZKP Toolkit...")
    
    try:
        import zkp_toolkit
        print("✅ ZKP toolkit imported successfully")
        
        # Test Schnorr key generation
        sk_hex, pk_hex = zkp_toolkit.generate_schnorr_keys_ffi()
        print(f"✅ Schnorr keys generated: PK={pk_hex[:16]}...")
        
        # Test Protostar proof generation
        test_data = "test_computation_data_hash_12345"
        proof = zkp_toolkit.generate_protostar_proof_ffi(test_data)
        print(f"✅ Protostar proof generated: {proof[:32]}...")
          # Test Schnorr proof generation (needs to be valid hex)
        challenge = "abcdef123456789012345678901234567890abcdef123456789012345678901234"
        schnorr_proof = zkp_toolkit.generate_schnorr_proof_ffi(sk_hex, pk_hex, challenge)
        print(f"✅ Schnorr proof generated: {schnorr_proof[:32]}...")
        
        return True
    except Exception as e:
        print(f"❌ ZKP toolkit test failed: {e}")
        return False

def test_data_loading():
    """Test data loading and partitioning"""
    print("\n🧪 Testing Data Loading...")
    
    try:
        from fl_system.data.utils import CLIENT_PARTITIONS
        print("✅ Data utils imported successfully")
        
        print(f"✅ Number of client partitions: {len(CLIENT_PARTITIONS)}")
        
        for i, ((X_train, y_train), (X_test, y_test)) in enumerate(CLIENT_PARTITIONS):
            print(f"  Client {i}: Train={X_train.shape}, Test={X_test.shape}")
        
        # Verify data shapes and types
        (X_train, y_train), (X_test, y_test) = CLIENT_PARTITIONS[0]
        assert isinstance(X_train, np.ndarray), "X_train should be numpy array"
        assert isinstance(y_train, np.ndarray), "y_train should be numpy array"
        assert len(X_train) > 0, "Training data should not be empty"
        
        print("✅ Data partitioning working correctly")
        return True
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def test_client_creation():
    """Test ZKFlowerClient creation and basic functionality"""
    print("\n🧪 Testing Client Creation...")
    
    try:
        from fl_system.client_impl.zk_client import ZkFlowerClient
        from fl_system.data.utils import CLIENT_PARTITIONS
        from sklearn.linear_model import LogisticRegression
        
        print("✅ Client imports successful")
        
        # Get data for first client
        (X_train, y_train), (X_test, y_test) = CLIENT_PARTITIONS[0]
        
        # Create model
        model = LogisticRegression(random_state=42, max_iter=100)
        
        # Create client
        client = ZkFlowerClient(
            client_id=0,
            model=model,
            x_train=X_train,
            y_train=y_train,
            x_test=X_test,
            y_test=y_test
        )
        
        print("✅ ZkFlowerClient created successfully")
        print(f"✅ Client ID: {client.client_id}")
        print(f"✅ Client Schnorr PK: {client.schnorr_pk_hex[:16]}...")
        
        # Test get_parameters
        initial_params = client.get_parameters({})
        print(f"✅ get_parameters returned {len(initial_params)} parameter arrays")
          # Test authentication (needs to be valid hex)
        challenge = "abcdef123456789012345678901234567890abcdef123456789012345678901234"
        pk, proof = client.get_authentication_details(challenge)
        print(f"✅ Authentication proof generated: {proof[:32]}...")
        
        return True
    except Exception as e:
        print(f"❌ Client creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_creation():
    """Test ZkProofStrategy creation"""
    print("\n🧪 Testing Strategy Creation...")
    
    try:
        from fl_system.strategy.zk_strategy import ZkProofStrategy
        
        print("✅ Strategy imports successful")
        
        # Create strategy
        strategy = ZkProofStrategy()
        print("✅ ZkProofStrategy created successfully")
        
        # Check strategy attributes
        assert hasattr(strategy, 'authorized_client_pks'), "Strategy should have authorized_client_pks"
        assert hasattr(strategy, 'current_round_metrics'), "Strategy should have current_round_metrics"
        
        print("✅ Strategy attributes verified")
        return True
    except Exception as e:
        print(f"❌ Strategy creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_training():
    """Test basic model training functionality"""
    print("\n🧪 Testing Model Training...")
    
    try:
        from fl_system.client_impl.zk_client import ZkFlowerClient
        from fl_system.data.utils import CLIENT_PARTITIONS
        from sklearn.linear_model import LogisticRegression
        
        # Get data for first client
        (X_train, y_train), (X_test, y_test) = CLIENT_PARTITIONS[0]
        
        # Create model and client
        model = LogisticRegression(random_state=42, max_iter=100)
        client = ZkFlowerClient(0, model, X_train, y_train, X_test, y_test)
        
        # Get initial parameters
        initial_params = client.get_parameters({})        # Simulate training round
        config = {"server_round": 1}
        fit_results, num_examples, metrics = client.fit(initial_params, config)
        
        print(f"✅ Training completed: {num_examples} examples used")
        print(f"✅ Fit results: {len(fit_results)} parameter arrays")
        print(f"✅ ZKP proof in metrics: {'protostar_proof' in metrics}")
        
        # Test evaluation
        loss, num_test, eval_metrics = client.evaluate(fit_results, config)
        print(f"✅ Evaluation completed: loss={loss:.4f}, accuracy={eval_metrics.get('accuracy', 'N/A'):.4f}")
        
        return True
    except Exception as e:
        print(f"❌ Model training test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all system tests"""
    print("🚀 Starting Complete Federated Learning ZKP System Test\n")
    
    tests = [
        ("ZKP Toolkit", test_zkp_toolkit),
        ("Data Loading", test_data_loading),
        ("Client Creation", test_client_creation),
        ("Strategy Creation", test_strategy_creation),
        ("Model Training", test_model_training),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("🎯 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:8} | {test_name}")
        if success:
            passed += 1
    
    print("-"*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for federated learning with ZKP.")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the errors above.")
    
    print("="*60)

if __name__ == "__main__":
    main()