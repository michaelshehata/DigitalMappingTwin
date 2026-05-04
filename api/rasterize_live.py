# api/rasterize_live.py

import numpy as np


def create_uniform_raster(value, shape):
    """
    Create raster filled with a single value
    """
    return np.full(shape, value, dtype=np.float32)


def inject_live_data(X, live_data):
    """
    Replace temperature channel in feature stack
    Assumes:
    X shape = (H, W, 5)
    index 3 = temperature
    """

    H, W, _ = X.shape

    temp_raster = create_uniform_raster(live_data["temperature"], (H, W))

    X_live = X.copy()
    X_live[:, :, 3] = temp_raster

    return X_live