use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList};
use super::{schnorr, protostar, protogalaxy, types};

#[pyfunction]
pub fn generate_schnorr_keys_ffi() -> PyResult<(String, String)> {
    let (sk, pk) = schnorr::generate_schnorr_keys();
    Ok((hex::encode(sk), hex::encode(pk)))
}

#[pyfunction]
pub fn generate_schnorr_proof_ffi(sk_hex: String, pk_hex: String, challenge_hex: String) -> PyResult<Py<PyBytes>> {
    let sk = hex::decode(sk_hex).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid sk_hex: {}", e)))?;
    let pk = hex::decode(pk_hex).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid pk_hex: {}", e)))?;
    let challenge = hex::decode(challenge_hex).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid challenge_hex: {}", e)))?;
    
    let proof = schnorr::generate_schnorr_proof(&sk, &pk, &challenge);
    Python::with_gil(|py| Ok(PyBytes::new(py, &proof).into()))
}

#[pyfunction]
pub fn verify_schnorr_proof_ffi(pk_hex: String, proof_bytes: &PyBytes, challenge_hex: String) -> PyResult<bool> {
    let pk = hex::decode(pk_hex).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid pk_hex: {}", e)))?;
    let proof = proof_bytes.as_bytes().to_vec();
    let challenge = hex::decode(challenge_hex).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid challenge_hex: {}", e)))?;
    
    Ok(schnorr::verify_schnorr_proof(&pk, &proof, &challenge))
}

#[pyfunction]
pub fn generate_protostar_proof_ffi(computation_data_str: String) -> PyResult<Py<PyBytes>> {
    let proof = protostar::generate_protostar_proof(&types::ComputationData::from(computation_data_str));
    Python::with_gil(|py| Ok(PyBytes::new(py, &proof).into()))
}

#[pyfunction]
pub fn verify_and_aggregate_protogalaxy_ffi(proof_list_py: &PyList) -> PyResult<Py<PyBytes>> {
    let mut proofs: Vec<types::ProofBytes> = Vec::new();
    for proof_py_bytes_obj in proof_list_py.iter() {
        let proof_py_bytes: &PyBytes = proof_py_bytes_obj.downcast()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!("Expected PyBytes in list: {}", e)))?;
        proofs.push(proof_py_bytes.as_bytes().to_vec());
    }

    match protogalaxy::verify_and_aggregate_protogalaxy(proofs) {
        Ok(aggregated_proof) => Python::with_gil(|py| Ok(PyBytes::new(py, &aggregated_proof).into())),
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(e)),
    }
}