# convert live data → raster

import numpy as np

def inject_live_data(X, live_data):

    X_live = X.copy()

    # temperature is index 3
    X_live[:, :, 3] = live_data["temperature"]

    return X_live