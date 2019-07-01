"""
    ...
"""

from __future__ import print_function
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# ---------------
class Model(nn.Module):
    """
    ...
    """

    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(8, 4)
        self.linear2 = nn.Linear(4, 1)

    def forward(self, x):
        x = self.linear1(x)
        x = torch.relu(x)
        x = self.linear2(x)
        x = torch.sigmoid(x)
        return x

# ---------------
def Generator():
    data = pd.read_csv("../../datasets/pulsar-star/pulsar_stars.csv")
    X, y = np.asarray(data.iloc[:, :8].values), np.asarray(data['target_class'].values)
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.10, random_state=42, stratify=y)
    X_train, X_valid = torch.tensor(X_train).float(), torch.tensor(X_valid).float()
    y_train, y_valid = torch.tensor(y_train).float(), torch.tensor(y_valid).float()
    return (X_train, X_valid, y_train, y_valid)

# ---------------
def train(data, model, optimizer, criterion, batch_size, max_epochs):
    train_curve, test_curve = [], []
    X_train, X_valid, y_train, y_valid = data
    for epoch in range(max_epochs):
        print("Epoch: " + str(epoch+1))
        """ Train """
        model.train()
        loss = train_step(X_train, y_train, model, optimizer, criterion, 
                            batch_size, train=True)
        train_curve.append(loss)

        """ Validation """
        model.eval()
        with torch.set_grad_enabled(False):
            loss = train_step(X_valid, y_valid, model, optimizer, criterion, 
                            batch_size, train=False)
        test_curve.append(loss)
        print("\t loss: " + str(loss))
    return model, (train_curve, test_curve)


# ---------------
def train_step(X, y, model, optimizer, criterion, batch_size, train):
        sum_loss, n_steps = 0, 0
        indices = np.arange(X.size(0))
        np.random.shuffle(indices)
        for i in range(0, len(X)-batch_size, batch_size):
            optimizer.zero_grad()
            idx = indices[i:i+batch_size]
            batch = X[idx].view(batch_size, -1)
            yhat = model(batch)  # N x D
            if train:
                loss = criterion(yhat, y[idx].unsqueeze(-1))
                sum_loss += loss.item()
                loss.backward()
                optimizer.step()
            else:
                yhat = yhat >= 0.5
                loss = (yhat != y[idx].unsqueeze(-1).byte()).sum().float()/yhat.size(0)
                sum_loss += loss.data
            n_steps += 1
        return (sum_loss/n_steps)

# ---------------
def plot_curves(test_curve, save=False):
    """ Plot train- and validation curves """
    test_curve = np.asarray(test_curve)
    epochs = np.arange(len(test_curve))
    plt.plot(epochs, test_curve)
    plt.legend()
    plt.show()
    if save: plt.savefig('results/valid-curves')
    plt.show()

# ---------------
if __name__ == "__main__":
    batch_size = 32
    data = Generator()
    model = Model().float()
    
    max_epochs = 30
    batch_size = 128
    criterion = nn.BCELoss()

    optimizer = torch.optim.Adam(nn.ParameterList(model.parameters()))
    model, curves = train(data, model, optimizer, criterion, batch_size, max_epochs)
    torch.save(model.state_dict(),"model.pt")
    plot_curves(curves[1])




















