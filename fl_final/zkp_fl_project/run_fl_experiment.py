#!/usr/bin/env python3
"""
Example runner for Federated Learning with ZKP Integration
This shows how to actually run the federated learning system with 2 clients and ZKP proofs.
"""

import sys
import os
import threading
import time
from multiprocessing import Process

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
fl_system_path = os.path.join(project_root, 'fl_system')
sys.path.append(project_root)
sys.path.append(fl_system_path)

import flwr as fl
from sklearn.linear_model import LogisticRegression

def run_server():
    """Run the federated learning server with ZKP strategy"""
    print("🚀 Starting Federated Learning Server with ZKP Strategy...")
    
    from fl_system.strategy.zk_strategy import ZkProofStrategy
    
    # Create ZKP-enabled strategy
    strategy = ZkProofStrategy(
        fraction_fit=1.0,  # Use all available clients for training
        fraction_evaluate=1.0,  # Use all clients for evaluation
        min_fit_clients=2,  # Wait for at least 2 clients
        min_evaluate_clients=2,
        min_available_clients=2,
    )
    
    # Start server
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
    )

def run_client(client_id: int):
    """Run a federated learning client with ZKP"""
    print(f"🤖 Starting Client {client_id} with ZKP integration...")
    
    from fl_system.client_impl.zk_client import ZkFlowerClient
    from fl_system.data.utils import CLIENT_PARTITIONS
    
    # Get data for this client
    (X_train, y_train), (X_test, y_test) = CLIENT_PARTITIONS[client_id]
    
    # Create model
    model = LogisticRegression(random_state=42, max_iter=100)
    
    # Create ZKP-enabled client
    client = ZkFlowerClient(
        client_id=client_id,
        model=model,
        x_train=X_train,
        y_train=y_train,
        x_test=X_test,
        y_test=y_test
    )
    
    # Set environment variable for the client
    os.environ["CLIENT_ID"] = str(client_id)
    
    # Connect to server
    fl.client.start_numpy_client(
        server_address="localhost:8080",
        client=client
    )

def main():
    """Main function to orchestrate the federated learning experiment"""
    print("🎯 Federated Learning with Zero-Knowledge Proofs")
    print("=" * 60)
    print("This example will:")
    print("- Start a FL server with ZKP verification strategy")
    print("- Launch 2 clients with ZKP proof generation")
    print("- Run 3 rounds of federated training")
    print("- Each client generates ZKP proofs for their computations")
    print("- Server verifies and aggregates proofs")
    print("=" * 60)
    
    choice = input("\nStart the experiment? (y/n): ").strip().lower()
    if choice != 'y':
        print("Experiment cancelled.")
        return
    
    try:
        # Start server in a separate process
        print("\n📡 Starting server...")
        server_process = Process(target=run_server)
        server_process.start()
        
        # Give server time to start
        time.sleep(3)
        
        # Start clients in separate processes
        client_processes = []
        for client_id in range(2):  # We have 2 client partitions
            print(f"\n🤖 Starting client {client_id}...")
            client_process = Process(target=run_client, args=(client_id,))
            client_process.start()
            client_processes.append(client_process)
            time.sleep(1)  # Stagger client starts
        
        # Wait for clients to complete
        for client_process in client_processes:
            client_process.join()
        
        # Cleanup
        print("\n🏁 Experiment completed!")
        print("All clients have finished their federated learning rounds.")
        print("ZKP proofs were generated and verified throughout the process.")
        
        server_process.terminate()
        server_process.join()
        
    except KeyboardInterrupt:
        print("\n⚠️ Experiment interrupted by user")
        # Cleanup processes
        if 'server_process' in locals():
            server_process.terminate()
        for process in client_processes:
            process.terminate()
    except Exception as e:
        print(f"\n❌ Error during experiment: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
