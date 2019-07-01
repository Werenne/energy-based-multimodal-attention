"""
    ...
"""

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split


# ---------------
def get_pulsar_data():
    data = pd.read_csv("../datasets/pulsar.csv")
    X, y = np.asarray(data.iloc[:, :8].values), np.asarray(data['target_class'].values)
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.33,
                        random_state=42, stratify=y)
    X_train, X_valid = torch.tensor(X_train).float(), torch.tensor(X_valid).float()
    y_train, y_valid = torch.tensor(y_train).float(), torch.tensor(y_valid).float()
    return (X_train, X_valid, y_train, y_valid)


# ---------------
def apply_corruption(X, noise):
    def add_noise(x, noise=0.01):
        x_ = x.data.numpy()
        noise = np.random.uniform(low=-noise, high=noise, size=np.shape(x_))
        out = np.add(x_, noise)
        return torch.from_numpy(out).float()

    if noise == 0:
        return X
    a = int(X.size(0)/2)
    b = int(X.size(0)/6)
    for j in range(X.size(1)):
        if j < 4:
            X[a:a+b,j] = add_noise(X[a:a+b,j], noise)
        else:
            X[a+b:a+2*b,j] = add_noise(X[a+b:a+2*b,j], noise)
        X[a+2*b:,j] = add_noise(X[a+2*b:,j], noise)
    return X


# ---------------
def split_corruption(X):
    a = int(X.size(0)/2)
    b = int(X.size(0)/6)
    return X[:a], X[a:a+b], X[a+b:a+2*b], X[a+2*b:]








































