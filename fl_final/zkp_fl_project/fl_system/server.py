import flwr as fl
from flwr.common import Metrics
from typing import List, Tuple, Optional, Dict, Union
from sklearn.linear_model import LogisticRegression
import numpy as np
import argparse

from strategy.zk_strategy import ZkProofStrategy, live_display # For control panel
from data.utils import X_test_global, y_test_global, NUM_CLIENTS # Global test set
from models.linear_regression import set_model_params

# Global model for central evaluation
GLOBAL_MODEL = LogisticRegression(solver='liblinear', warm_start=True) 

# Store client PKs here for the demo (in real system, this is from secure registration)
# This is a hack for the demo because Flower's ClientProxy doesn't easily expose custom attributes like schnorr_pk_hex
# that would be set by the ZkFlowerClient instance.
# We will populate this dictionary in `client_fn` when clients are "created" for simulation.
DEMO_AUTHORIZED_PKS: Dict[str, str] = {}


def get_evaluate_fn(model: LogisticRegression, X_test, y_test):
    """Return an evaluation function for server-side evaluation."""
    def evaluate(
        server_round: int, parameters: fl.common.Parameters, config: Dict[str, fl.common.Scalar]
    ) -> Optional[Tuple[float, Dict[str, fl.common.Scalar]]]:
        set_model_params(model, parameters) # type: ignore
        
        # Ensure classes_ is set if model hasn't been fit before (e.g. first round from init_params)
        if not hasattr(model, 'classes_') or model.classes_ is None:
            model.classes_ = np.array([0, 1]) # Iris binary case

        loss = 0.0 # log_loss not directly applicable if only params, need predict_proba
        try:
            # Predict proba might fail if model is not sufficiently trained or dimensions mismatch
            # For simplicity, we'll rely on client-side evaluation reporting accuracy
            # or directly use score if possible (requires model to be 'fitted' state)
            accuracy = model.score(X_test, y_test)
        except Exception as e:
            # print(f"Server-side eval error: {e}")
            accuracy = 0.0 # Default if scoring fails

        print(f"Server-side evaluation round {server_round}, Accuracy: {accuracy:.4f}")
        return float(loss), {"accuracy": float(accuracy)} # Loss is dummy here
    return evaluate

def main():
    parser = argparse.ArgumentParser(description="Flower ZKP Server")
    parser.add_argument("--rounds", type=int, default=3, help="Number of FL rounds")
    parser.add_argument("--server-address", type=str, default="0.0.0.0:8080", help="Server address to bind")
    args = parser.parse_args()

    strategy = ZkProofStrategy(
        fraction_fit=1.0,  # Sample all clients for fit
        fraction_evaluate=1.0, # Sample all clients for evaluate
        min_fit_clients=NUM_CLIENTS,
        min_evaluate_clients=NUM_CLIENTS,
        min_available_clients=NUM_CLIENTS,
        evaluate_fn=get_evaluate_fn(GLOBAL_MODEL, X_test_global, y_test_global), # Server-side global eval
        # on_fit_config_fn=fit_config, # Can pass config to clients
    )
    
    # This part is for the DEMO to populate the authorized PKs for the strategy.
    # In a real system, the strategy would have access to a secure registry.
    # We create temporary client instances just to get their generated PKs.
    print("Pre-populating authorized PKs for demo strategy...")
    from client_impl.zk_client import ZkFlowerClient as ActualClient
    from data.utils import CLIENT_PARTITIONS
    
    temp_model = LogisticRegression()
    for i in range(NUM_CLIENTS):
        (x_train_c, y_train_c), (x_test_c, y_test_c) = CLIENT_PARTITIONS[i]
        temp_client_instance = ActualClient(i, temp_model, x_train_c, y_train_c, x_test_c, y_test_c)
        DEMO_AUTHORIZED_PKS[str(i)] = temp_client_instance.schnorr_pk_hex # Store cid -> pk_hex
        print(f"  Authorized PK for simulated client {i}: {temp_client_instance.schnorr_pk_hex[:10]}...")
    strategy.authorized_client_pks = DEMO_AUTHORIZED_PKS # Give to strategy

    print(f"Starting Flower ZKP Server at {args.server_address} for {args.rounds} rounds.")
    
    with live_display: # For the control panel
        fl.server.start_server(
            server_address=args.server_address,
            config=fl.server.ServerConfig(num_rounds=args.rounds),
            strategy=strategy,
        )
    print("Server finished.")


if __name__ == "__main__":
    main()