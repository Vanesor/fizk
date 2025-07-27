import os
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from flwr.server import ServerConfig
import flwr as fl
from flwr.server.strategy import FedAvg

# ======================
# Data Preparation
# ======================

def prepare_and_split(csv_file: str, client_name: str, test_size: float = 0.2):
    """
    Split the given CSV into train/test and save under client_datasets/<client_name>/
    """
    # Create client directory
    base_dir = os.path.join("client_datasets", client_name)
    os.makedirs(base_dir, exist_ok=True)

    # Paths
    train_path = os.path.join(base_dir, "train.csv")
    test_path = os.path.join(base_dir, "test.csv")

    # Only split if not already done
    if os.path.exists(train_path) and os.path.exists(test_path):
        print(f"[INFO] Skipping split for {client_name}, files exist.")
        return

    # Load full dataset
    df = pd.read_csv(csv_file)
    # Split
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)
    # Save
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print(f"[INFO] Split {csv_file} → {train_path}, {test_path}")


def prepare_all_clients():
    """
    Prepare datasets for 3 clients by splitting the provided CSV files.
    """
    mappings = [
        ("pima-indians-diabetes.csv", "client1"),
        ("heart.csv", "client2"),
        ("wdbc.csv", "client3"),
    ]
    for csv_file, client_name in mappings:
        prepare_and_split(csv_file, client_name)


# ======================
# Model Definition
# ======================

class Net(nn.Module):
    def __init__(self, input_size: int):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, 16)
        self.fc2 = nn.Linear(16, 8)
        self.fc3 = nn.Linear(8, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return torch.sigmoid(self.fc3(x))


# ======================
# Flower Client
# ======================

from flwr.client import Client

class FlowerClient(Client):
    def __init__(self, model, train_loader, test_loader, device):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.device = device
        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01)

    def get_parameters(self, ins):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]

    def fit(self, ins):
        self.set_parameters(ins.parameters)
        self.model.train()
        for data, target in self.train_loader:
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output.view(-1), target)
            loss.backward()
            self.optimizer.step()
        return self.get_parameters(ins), len(self.train_loader.dataset), {}

    def evaluate(self, ins):
        self.set_parameters(ins.parameters)
        self.model.eval()
        loss = 0.0
        correct = 0
        with torch.no_grad():
            for data, target in self.test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss += self.criterion(output.view(-1), target).item() * len(target)
                preds = (output.view(-1) > 0.5).float()
                correct += (preds == target).sum().item()
        loss /= len(self.test_loader.dataset)
        accuracy = correct / len(self.test_loader.dataset)
        return float(loss), len(self.test_loader.dataset), {"accuracy": float(accuracy)}

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)


# ======================
# Data Loader
# ======================

def load_client_data(client_id: int):
    """
    Load train/test for a given client and return DataLoaders and input size.
    """
    base = os.path.join("client_datasets", f"client{client_id}")
    train_df = pd.read_csv(os.path.join(base, "train.csv"))
    test_df = pd.read_csv(os.path.join(base, "test.csv"))

    X_train = train_df.iloc[:, :-1].values.astype("float32")
    y_train = train_df.iloc[:, -1].values.astype("float32")
    X_test = test_df.iloc[:, :-1].values.astype("float32")
    y_test = test_df.iloc[:, -1].values.astype("float32")

    train_loader = DataLoader(
        TensorDataset(torch.tensor(X_train), torch.tensor(y_train)),
        batch_size=32,
        shuffle=True,
    )
    test_loader = DataLoader(
        TensorDataset(torch.tensor(X_test), torch.tensor(y_test)),
        batch_size=32,
    )

    input_size = X_train.shape[1]
    return train_loader, test_loader, input_size


# ======================
# Flower Client Factory
# ======================

def client_fn(cid: str) -> fl.client.Client:
    client_id = int(cid) + 1
    train_loader, test_loader, input_size = load_client_data(client_id)
    model = Net(input_size)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    numpy_client = FlowerClient(model, train_loader, test_loader, device)
    return numpy_client.to_client()




# ======================
# Simulation
# ======================

from flwr.server import ServerConfig

def main():
    # Step 1: Prepare data for all clients
    prepare_all_clients()

    # Step 2: Configure and start simulation
    strategy = FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=3,
        min_evaluate_clients=3,
        min_available_clients=3,
    )

    fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=ServerConfig(num_rounds=3),
        strategy=strategy,
    )

if __name__ == "__main__":
    main()
