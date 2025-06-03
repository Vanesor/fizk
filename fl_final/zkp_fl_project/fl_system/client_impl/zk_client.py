import flwr as fl
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
import os
import hashlib
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Rust ZKP toolkit - direct import, no fallbacks
import zkp_toolkit

from models.linear_regression import get_model_parameters, set_model_params
from data.utils import CLIENT_PARTITIONS

CLIENT_ID = int(os.environ.get("CLIENT_ID", "0"))
(X_train, y_train), (X_test, y_test) = CLIENT_PARTITIONS[CLIENT_ID]


class ZkFlowerClient(fl.client.NumPyClient):
    def __init__(self, client_id: int, model: LogisticRegression, x_train, y_train, x_test, y_test):
        self.client_id = client_id
        self.model = model
        self.x_train, self.y_train = x_train, y_train
        self.x_test, self.y_test = x_test, y_test
        
        # Initialize model with some data to avoid "not fitted" error
        self.model.fit(self.x_train[:5], self.y_train[:5])  # Quick initial fit
        
        # ZKP-Schnorr: Client generates its key pair
        self.schnorr_sk_hex, self.schnorr_pk_hex = zkp_toolkit.generate_schnorr_keys_ffi()
        print(f"[Client {self.client_id}] Schnorr PK: {self.schnorr_pk_hex[:10]}...")

    def get_properties(self, config):
        """Flower client method to expose client properties including ZKP public key."""
        return {
            "schnorr_pk_hex": self.schnorr_pk_hex,
            "client_id": str(self.client_id)
        }

    def get_parameters(self, config):
        print(f"[Client {self.client_id}] get_parameters")
        return get_model_parameters(self.model)

    def fit(self, parameters, config):
        print(f"[Client {self.client_id}] fit_round {config.get('server_round', 'N/A')}")
        set_model_params(self.model, parameters)
        # Fit for a small number of epochs or iterations
        self.model.fit(self.x_train, self.y_train)
        
        # --- ZKP INTEGRATION POINT (Client-side proof of computation) ---
        # 1. Prepare computation data to be proven
        new_params = get_model_parameters(self.model)
        param_bytes = b"".join([arr.tobytes() for arr in new_params if isinstance(arr, np.ndarray)])
        computation_hash = hashlib.sha256(param_bytes).hexdigest()
        computation_data_for_zkp = f"client_{self.client_id}_round_{config.get('server_round', 'N/A')}_params_hash_{computation_hash}"

        # 2. Generate Protostar proof for the local training computation
        print(f"[Client {self.client_id}] Generating Protostar proof...")
        protostar_proof = zkp_toolkit.generate_protostar_proof_ffi(computation_data_for_zkp)
        # --- END ZKP INTEGRATION POINT ---

        fit_results = get_model_parameters(self.model)
        num_examples = len(self.x_train)
        
        # Return model parameters and the ZKP proof
        return fit_results, num_examples, {"protostar_proof": protostar_proof, "schnorr_pk_hex": self.schnorr_pk_hex}

    def evaluate(self, parameters, config):
        print(f"[Client {self.client_id}] evaluate")
        set_model_params(self.model, parameters)
        loss = log_loss(self.y_test, self.model.predict_proba(self.x_test))
        accuracy = self.model.score(self.x_test, self.y_test)
        return loss, len(self.x_test), {"accuracy": accuracy}

    def get_authentication_details(self, challenge_hex: str):
        """Generates Schnorr proof for a given challenge."""
        print(f"[Client {self.client_id}] Generating Schnorr auth proof for challenge: {challenge_hex[:10]}...")
        proof = zkp_toolkit.generate_schnorr_proof_ffi(
            self.schnorr_sk_hex, self.schnorr_pk_hex, challenge_hex
        )
        return self.schnorr_pk_hex, proof