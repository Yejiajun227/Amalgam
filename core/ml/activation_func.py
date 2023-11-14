import numpy as np
import pandas as pd


def sigmoid(x):
    # to avoid overflow encountered in exp
    if type(x) == np.ndarray:
        if len(x) > 0:
            y = []
            for xi in x:
                y.append(sigmoid(xi))
            y = np.array(y)
    elif type(x) == pd.DataFrame:
        y = sigmoid(x.values)
    else:
        if x >= 0:
            y = 1.0 / (1.0 + np.exp(-x))
        else:
            y = np.exp(x) / (np.exp(x) + 1.0)
    return np.clip(y, 0.0000000001, 0.9999999999)


