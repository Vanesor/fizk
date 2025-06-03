import flwr as fl
from sklearn.linear_model import LogisticRegression
import argparse
import os

from zk_client import ZkFlowerClient
from ..data.utils import CLIENT_PARTITIONS # Ensure CLIENT_PARTITIONS is loaded

def main():
    parser = argparse.ArgumentParser(description="Flower ZKP Client")
    parser.add_argument(
        "--client-id", type=int, required=True, help="Client ID (0-based)"
    )
    parser.add_argument(
        "--server-address", type=str, default="127.0.0.1:8080", help="Server address"
    )
    args = parser.parse_args()

    os.environ["CLIENT_ID"] = str(args.client_id) # For zk_client.py to pick up

    # Load client-specific data partition
    if args.client_id >= len(CLIENT_PARTITIONS):
        print(f"Error: Client ID {args.client_id} is out of bounds for {len(CLIENT_PARTITIONS)} partitions.")
        return
        
    (x_train_client, y_train_client), (x_test_client, y_test_client) = CLIENT_PARTITIONS[args.client_id]

    model = LogisticRegression(solver='liblinear', warm_start=True, max_iter=3) # Few iterations for FL rounds

    client = ZkFlowerClient(
        client_id=args.client_id,
        model=model,
        x_train=x_train_client,
        y_train=y_train_client,
        x_test=x_test_client,
        y_test=y_test_client,
    )
    
    print(f"Starting Client {args.client_id} connecting to {args.server_address}")
    fl.client.start_numpy_client(server_address=args.server_address, client=client)
    print(f"Client {args.client_id} finished.")

if __name__ == "__main__":
    main()