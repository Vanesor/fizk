from typing import Dict, List, Optional, Tuple, Union
from flwr.common import FitRes, Parameters, Scalar, FitIns, EvaluateIns
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg
import os
import hashlib
from rich.console import Console
from rich.table import Table
from rich.live import Live
from time import sleep, perf_counter # Added perf_counter
import json # Added for saving metrics


# Import the Rust ZKP toolkit
try:
    import zkp_toolkit  # Name from Cargo.toml lib.name
except ImportError:
    print("ERROR: zkp_toolkit_lib not found. Did you build the Rust code and install the wheel or use 'maturin develop'?")
    print("Attempting to use a mock ZKP toolkit for Python-only testing.")
    class MockZkpToolkit:
        def verify_schnorr_proof_ffi(self, pk, proof, ch): return True # Always true for mock
        def verify_and_aggregate_protogalaxy_ffi(self, proofs): return b"mock_aggregated_protogalaxy_proof"
        def generate_schnorr_keys_ffi(self): return ("mock_sk_hex", "mock_pk_hex")
        def generate_schnorr_proof_ffi(self, sk, pk, ch): return b"mock_schnorr_proof"
        def generate_protostar_proof_ffi(self, data): return b"mock_protostar_proof"
    zkp_toolkit = MockZkpToolkit()


# --- Control Panel Setup ---
console = Console()
overall_metrics_table = Table(title="Federated Learning ZKP Experiment - Overall Metrics")
overall_metrics_table.add_column("Round", style="cyan")
overall_metrics_table.add_column("Auth Success", style="green")
overall_metrics_table.add_column("Auth Fail", style="red")
overall_metrics_table.add_column("Proofs Aggregated", style="magenta")
overall_metrics_table.add_column("Aggregation Valid", style="green")
overall_metrics_table.add_column("Agg. Loss", style="yellow")
overall_metrics_table.add_column("Agg. Accuracy", style="blue")

live_display = Live(overall_metrics_table, console=console, refresh_per_second=1)
# --- End Control Panel Setup ---


class ZkProofStrategy(FedAvg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authorized_client_pks: Dict[str, str] = {} # Store cid -> pk_hex
        self.current_round_metrics = {} # For control panel
        self.history: List[Dict[str, Union[str, float, int]]] = [] # To store metrics for dashboard
        self.overall_start_time: Optional[float] = None
        self.round_start_time: Optional[float] = None
        self.metrics_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fl_metrics_log.json") # Save in project root

    def initialize_parameters(self, client_manager):
        # For real systems, PKs would be registered securely beforehand.
        # For this demo, we'll assume clients will send their PKs on first contact
        # and the server will "authorize" them.
        # A better approach: server has a pre-approved list of PKs.
        print("Strategy initialized. Waiting for clients to connect to get their PKs for 'authorization'.")
        print("In a real system, PKs should be pre-registered and verified.")
        self.overall_start_time = perf_counter() # Start overall timer
        # Initialize metrics file
        self._save_metrics_to_file() 
        return super().initialize_parameters(client_manager)

    def configure_fit(
        self, server_round: int, parameters: Parameters, client_manager # type: ignore
    ) -> List[Tuple[ClientProxy, FitIns]]:
        """Configure the next round of training."""
        self.round_start_time = perf_counter() # Start round timer
        auth_start_time = perf_counter()

        self.current_round_metrics = {
            "round": server_round,
            "auth_success": 0,
            "auth_fail": 0,
            "auth_time_sec": 0.0,
            "proofs_aggregated": 0,
            "aggregation_valid": "N/A",
            "proof_aggregation_time_sec": 0.0,
            "model_aggregation_time_sec": 0.0,
            "agg_loss": "N/A",
            "agg_accuracy": "N/A",
            "round_duration_sec": 0.0
        }
        console.print(f"\n--- Round {server_round} Starting ---", style="bold green")
        
        config = {}
        if self.on_fit_config_fn is not None:
            config = self.on_fit_config_fn(server_round)
        
        config["server_round"] = server_round # Pass round number to client

        fit_ins = FitIns(parameters, config)
        clients = client_manager.sample(
            num_clients=self.min_fit_clients, min_num_clients=self.min_fit_clients # type: ignore
        )

        # --- ZKP INTEGRATION POINT (Client Authentication) ---
        # COMMENT: Client Authentication using ZKP-Schnorr (can also be done at initial connection)
        # For each selected client, perform a Schnorr-based challenge-response authentication.
        authenticated_clients_for_round: List[Tuple[ClientProxy, FitIns]] = []
        for client_proxy in clients:
            try:
                challenge = os.urandom(16).hex() # Server generates a fresh challenge
                
                # This requires a custom method on the client to get its PK and respond to challenge
                # We need to call a custom client method. Flower doesn't support this directly in configure_fit.
                # This is a known limitation. A common workaround is to do auth during client registration
                # or by having client send proof with `fit` results (less ideal for pre-round auth).
                # For this demo, we'll *simulate* it by accessing client's PK if stored, or assuming success.
                
                # A more robust way, if client implements `get_properties` to expose PK:
                # client_props = client_proxy.get_properties(ins={}, timeout=10)
                # client_pk_hex = client_props.get("schnorr_pk_hex")

                # SIMPLIFIED: Assume we get PK and proof (actual call needs custom Flower client method)
                # Let's pretend the client object (if it were the real one) has these:
                if not hasattr(client_proxy, 'schnorr_pk_hex'): # First time seeing this client proxy in strategy
                    # In a real scenario, client sends PK during registration or first connect.
                    # Here, we simulate that the client's zk_client.py would have `schnorr_pk_hex`
                    # For Flower's ClientProxy, this attribute won't exist.
                    # We'll pre-populate authorized_client_pks for the demo.
                    # THIS PART IS A HACK FOR THE DEMO due to Flower's proxy limitations.
                    # We'll populate self.authorized_client_pks in server.py after clients are known.
                    pass # Handled in server.py for demo purposes.

                client_pk_hex = self.authorized_client_pks.get(client_proxy.cid)
                if not client_pk_hex:
                    console.print(f"[Server] Client {client_proxy.cid} PK not known/authorized. Skipping.", style="orange1")
                    self.current_round_metrics["auth_fail"] += 1
                    continue

                # This is where we'd send challenge to client and get proof.
                # For demo, assume client's fit() will return auth proof or it's pre-auth.
                # Let's simulate a successful verification for now.
                # schnorr_proof_bytes = ... get from client ...
                # is_auth = zkp_toolkit.verify_schnorr_proof_ffi(client_pk_hex, schnorr_proof_bytes, challenge)
                is_auth = True # MOCKING THE ACTUAL RPC CALL FOR AUTH PROOF

                if is_auth:
                    console.print(f"[Server] Client {client_proxy.cid} authenticated (mocked).", style="green")
                    authenticated_clients_for_round.append((client_proxy, fit_ins))
                    self.current_round_metrics["auth_success"] += 1
                else:
                    console.print(f"[Server] Client {client_proxy.cid} authentication FAILED. Skipping.", style="red")
                    self.current_round_metrics["auth_fail"] += 1
            except Exception as e:
                console.print(f"[Server] Error authenticating client {client_proxy.cid}: {e}", style="red")
                self.current_round_metrics["auth_fail"] += 1
        
        auth_duration = perf_counter() - auth_start_time
        self.current_round_metrics["auth_time_sec"] = round(auth_duration, 4)

        if not authenticated_clients_for_round:
            console.print("[Server] No clients authenticated for this round.", style="bold red")
        
        # --- END ZKP INTEGRATION POINT ---
        return authenticated_clients_for_round


    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        
        if not results:
            console.print("[Server] aggregate_fit: No results to aggregate.", style="orange1")
            if self.round_start_time:
                round_duration = perf_counter() - self.round_start_time
                self.current_round_metrics["round_duration_sec"] = round(round_duration, 4)
            self._log_round_metrics() # Log metrics even if no results
            return None, {}

        # --- ZKP INTEGRATION POINT (Server-side aggregation of proofs) ---
        # COMMENT: Server-side aggregation and verification of proofs using ProtoGalaxy
        proof_aggregation_start_time = perf_counter()
        
        valid_client_proofs: List[bytes] = []
        results_with_valid_proofs: List[Tuple[ClientProxy, FitRes]] = []

        for client_proxy, fit_res in results:
            # Extract Protostar proof from client's FitRes metrics
            protostar_proof = fit_res.metrics.get("protostar_proof")
            if protostar_proof and isinstance(protostar_proof, bytes):
                valid_client_proofs.append(protostar_proof)
                results_with_valid_proofs.append((client_proxy, fit_res)) # Keep track of which results map to these proofs
                console.print(f"[Server] Received Protostar proof from client {client_proxy.cid} (len: {len(protostar_proof)}).", style="dim blue")
            else:
                console.print(f"[Server] Client {client_proxy.cid} did not provide a valid Protostar proof. Excluding.", style="orange1")
        
        aggregated_zkp_proof = None
        aggregation_successful = False
        if valid_client_proofs:
            self.current_round_metrics["proofs_aggregated"] = len(valid_client_proofs)
            try:
                console.print(f"[Server] Aggregating {len(valid_client_proofs)} client proofs using ProtoGalaxy...", style="magenta")
                aggregated_zkp_proof = zkp_toolkit.verify_and_aggregate_protogalaxy_ffi(valid_client_proofs)
                # If verify_and_aggregate_protogalaxy_ffi returns successfully, all individual proofs were valid
                # and successfully aggregated.
                console.print(f"[Server] ProtoGalaxy aggregation successful! Agg. proof len: {len(aggregated_zkp_proof)}", style="bold green")
                aggregation_successful = True
                self.current_round_metrics["aggregation_valid"] = "✅"
            except Exception as e:
                console.print(f"[Server] ProtoGalaxy aggregation FAILED: {e}", style="bold red")
                results_with_valid_proofs = [] 
                self.current_round_metrics["aggregation_valid"] = "❌"
        else:
            console.print("[Server] No valid client proofs received for ProtoGalaxy aggregation.", style="orange1")
            self.current_round_metrics["aggregation_valid"] = "N/A (No proofs)"

        proof_aggregation_duration = perf_counter() - proof_aggregation_start_time
        self.current_round_metrics["proof_aggregation_time_sec"] = round(proof_aggregation_duration, 4)

        # --- END ZKP INTEGRATION POINT ---

        model_aggregation_start_time = perf_counter()
        if aggregation_successful and results_with_valid_proofs:
            aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results_with_valid_proofs, [])
            console.print(f"[Server] Model parameters aggregated from {len(results_with_valid_proofs)} ZKP-verified clients.", style="green")
        else:
            # No valid proofs or aggregation failed, return no parameters
            console.print("[Server] No model parameters aggregated due to ZKP failure or lack of proofs.", style="orange1")
            aggregated_parameters, aggregated_metrics = None, {}
        
        model_aggregation_duration = perf_counter() - model_aggregation_start_time
        self.current_round_metrics["model_aggregation_time_sec"] = round(model_aggregation_duration, 4)

        if self.round_start_time:
            round_duration = perf_counter() - self.round_start_time
            self.current_round_metrics["round_duration_sec"] = round(round_duration, 4)

        # Update control panel before returning
        overall_metrics_table.add_row(
            str(self.current_round_metrics["round"]),
            str(self.current_round_metrics["auth_success"]),
            str(self.current_round_metrics["auth_fail"]),
            str(self.current_round_metrics["proofs_aggregated"]),
            str(self.current_round_metrics["aggregation_valid"]),
            str(self.current_round_metrics["agg_loss"]),
            str(self.current_round_metrics["agg_accuracy"])
        )
        live_display.update(overall_metrics_table)
        
        self._log_round_metrics() # Save metrics for this round

        return aggregated_parameters, aggregated_metrics

    def aggregate_evaluate(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, EvaluateIns]], # Should be EvaluateRes
        failures: List[Union[Tuple[ClientProxy, EvaluateIns], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """Aggregate evaluation results."""
        loss_aggregated, metrics_aggregated = super().aggregate_evaluate(server_round, results, failures) # type: ignore
        
        current_loss = "N/A"
        current_accuracy = "N/A"

        if loss_aggregated is not None:
            current_loss = f"{loss_aggregated:.4f}"
            self.current_round_metrics["agg_loss"] = current_loss
        if metrics_aggregated and "accuracy" in metrics_aggregated:
            current_accuracy = f"{metrics_aggregated['accuracy']:.4f}"
            self.current_round_metrics["agg_accuracy"] = current_accuracy
        
        console.print(f"--- Round {server_round} Evaluation ---", style="bold blue")
        console.print(f"Aggregated Loss: {current_loss}, Aggregated Accuracy: {current_accuracy}")

        # Update history with evaluation results for the current round
        if self.history and self.history[-1].get("round") == server_round:
            self.history[-1]["agg_loss"] = self.current_round_metrics.get("agg_loss", "N/A")
            self.history[-1]["agg_accuracy"] = self.current_round_metrics.get("agg_accuracy", "N/A")
            # No need to call _save_metrics_to_file() here, it's called in _log_round_metrics which is called after fit
            # However, if evaluate is the last step, we might want to save here.
            # For simplicity, we assume fit is always followed by evaluate or that _log_round_metrics in fit is sufficient.

        # Update the Rich table if it's still active
        # This requires finding the correct row to update, which can be tricky with add_row.
        # A simpler way for the live display is to rely on the next aggregate_fit call to update the table.
        # Or, if evaluate is the final step of a round, update it here.
        # For now, we will update the table directly if it's the last action for the round.
        # This is a bit of a simplification as the table might not be displayed if only evaluate is called.
        if live_display.is_started: # Check if live display is active
            # Find the row for the current round and update it
            # This is not straightforward with Rich Table.add_row. 
            # It's better to rebuild the table or manage rows more directly if frequent updates are needed.
            # For this iteration, we will rely on the next aggregate_fit to update the table with these eval metrics.
            # Or, we can update the current_round_metrics and the next aggregate_fit will pick it up.
            pass # Rely on aggregate_fit to update the table with these metrics

        return loss_aggregated, metrics_aggregated

    def _log_round_metrics(self):
        """Logs the metrics for the current round to history and saves to file."""
        # Ensure all expected keys are present, even if N/A
        final_metrics_for_round = {
            "round": self.current_round_metrics.get("round", "N/A"),
            "auth_success": self.current_round_metrics.get("auth_success", 0),
            "auth_fail": self.current_round_metrics.get("auth_fail", 0),
            "auth_time_sec": self.current_round_metrics.get("auth_time_sec", 0.0),
            "proofs_aggregated": self.current_round_metrics.get("proofs_aggregated", 0),
            "aggregation_valid": self.current_round_metrics.get("aggregation_valid", "N/A"),
            "proof_aggregation_time_sec": self.current_round_metrics.get("proof_aggregation_time_sec", 0.0),
            "model_aggregation_time_sec": self.current_round_metrics.get("model_aggregation_time_sec", 0.0),
            "agg_loss": self.current_round_metrics.get("agg_loss", "N/A"),
            "agg_accuracy": self.current_round_metrics.get("agg_accuracy", "N/A"),
            "round_duration_sec": self.current_round_metrics.get("round_duration_sec", 0.0)
        }
        self.history.append(final_metrics_for_round)
        self._save_metrics_to_file()

    def _save_metrics_to_file(self):
        """Saves the history of metrics to a JSON file."""
        if self.overall_start_time:
            total_duration = perf_counter() - self.overall_start_time
            data_to_save = {
                "overall_start_time_iso": self.overall_start_time, 
                "total_duration_sec_so_far": round(total_duration, 4),
                "rounds_history": self.history
            }
        else:
            data_to_save = {"rounds_history": self.history}

        try:
            with open(self.metrics_file_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except IOError as e:
            console.print(f"[Server] Error saving metrics to {self.metrics_file_path}: {e}", style="bold red")
