// src/lib.rs
use pyo3::prelude::*;

mod ffi; // This now contains the #[pymodule] zkp_toolkit
mod schnorr;
mod protostar;
mod protogalaxy;
mod types;

// Re-export the module defined in ffi.rs
#[pymodule]
fn zkp_toolkit(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ffi::generate_schnorr_keys_ffi, m)?)?;
    m.add_function(wrap_pyfunction!(ffi::generate_schnorr_proof_ffi, m)?)?;
    m.add_function(wrap_pyfunction!(ffi::verify_schnorr_proof_ffi, m)?)?;
    m.add_function(wrap_pyfunction!(ffi::generate_protostar_proof_ffi, m)?)?;
    m.add_function(wrap_pyfunction!(ffi::verify_and_aggregate_protogalaxy_ffi, m)?)?;
    Ok(())
}