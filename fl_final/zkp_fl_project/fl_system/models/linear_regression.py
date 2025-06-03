from sklearn.linear_model import LogisticRegression
import numpy as np

def get_model_parameters(model: LogisticRegression):
    """Returns the paramters of a sklearn LogisticRegression model."""
    if hasattr(model, 'coef_') and model.coef_ is not None:
        params = [
            model.coef_,
            model.intercept_,
        ]
    else: # Model not fitted
        params = []
    return params

def set_model_params(model: LogisticRegression, params) -> LogisticRegression:
    """Sets the parameters of a sklean LogisticRegression model."""
    if not params: # Not fitted yet
        return model
    model.coef_ = params[0]
    model.intercept_ = params[1]
    # This is crucial for sklearn: make sure classes_ is set if you load params before fitting
    # For this simple binary case with Iris (after filtering), classes are 0 and 1
    if not hasattr(model, 'classes_') or model.classes_ is None:
         model.classes_ = np.array([0, 1])
    return model