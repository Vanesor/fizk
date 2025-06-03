# ZKP Federated Learning Project

A privacy-preserving federated learning system using zero-knowledge proofs.

## Components

- **fl_system/**: Python-based federated learning implementation using Flower
- **zkp_toolkit/**: Rust-based zero-knowledge proof library

## Setup

### Python Environment
```bash
cd fl_system
pip install -r requirements.txt
```

### Rust Build
```bash
cd zkp_toolkit
cargo build --release
```

## Usage

1. Build the Rust ZKP toolkit
2. Run the federated learning system
3. Privacy-preserving model training with ZK proofs

## Architecture

- Client implementations with ZK proof generation
- Server coordination with proof verification
- Multiple ZKP schemes (Schnorr, Protogalaxy, Protostar)
