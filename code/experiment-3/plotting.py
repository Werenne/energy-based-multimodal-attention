import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import rc
import seaborn as sns
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('text', usetex=True)
plt.style.use('seaborn-poster') 
plt.style.use('ggplot')
from sklearn.metrics import confusion_matrix
from main import evaluation, model_evaluation
from data import white_noise
import torch


# ---------------
def print_confusion_matrix(yhat, y):
    cm = confusion_matrix(y, yhat)
    classes = [0, 1]
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print(cm)
    print()


# ---------------
def plot_curves(curves, params, save=False):
    train_curve, valid_curve = curves['model-with'][params][0,:], curves['model-with'][params][1,:]
    epochs = np.arange(len(train_curve))
    plt.plot(epochs, train_curve, label="Train")
    plt.plot(epochs, valid_curve, label="Validation")
    plt.xlabel('epochs', fontsize=18)
    plt.ylabel('cross-entropy loss', fontsize=18)
    plt.tick_params(axis='both', which='major', labelsize=11)
    plt.legend()
    if save: plt.savefig('results/curves')
    plt.show()


# ---------------
def refined_matrix(y, classes, indic):
    mat = np.zeros((6,2))
    mat[0,0] = int(((y == 1) * (classes == 1) * (indic[:,0] == 0) * (indic[:,1] == 0)).sum().data.numpy())
    mat[0,1] = int(((y == 1) * (classes == 0) * (indic[:,0] == 0) * (indic[:,1] == 0)).sum().data.numpy())
    
    mat[1,0] = int(((y == 1) * (classes == 1) * (indic[:,0] == 1) * (indic[:,1] == 0)).sum().data.numpy())
    mat[1,1] = int(((y == 1) * (classes == 0) * (indic[:,0] == 1) * (indic[:,1] == 0)).sum().data.numpy())

    mat[2,0] = int(((y == 1) * (classes == 1) * (indic[:,0] == 0) * (indic[:,1] == 1)).sum().data.numpy())
    mat[2,1] = int(((y == 1) * (classes == 0) * (indic[:,0] == 0) * (indic[:,1] == 1)).sum().data.numpy())

    mat[3,0] = int(((y == 0) * (classes == 0) * (indic[:,0] == 0) * (indic[:,1] == 0)).sum().data.numpy())
    mat[3,1] = int(((y == 0) * (classes == 1) * (indic[:,0] == 0) * (indic[:,1] == 0)).sum().data.numpy())

    mat[4,0] = int(((y == 0) * (classes == 0) * (indic[:,0] == 1) * (indic[:,1] == 0)).sum().data.numpy())
    mat[4,1] = int(((y == 0) * (classes == 1) * (indic[:,0] == 1) * (indic[:,1] == 0)).sum().data.numpy())

    mat[5,0] = int(((y == 0) * (classes == 0) * (indic[:,0] == 0) * (indic[:,1] == 1)).sum().data.numpy())
    mat[5,1] = int(((y == 0) * (classes == 1) * (indic[:,0] == 0) * (indic[:,1] == 1)).sum().data.numpy())
    print(mat/np.sum(mat, axis=1, keepdims=True))
    print()


# ---------------
def plot_distribution(model, X, indic, save=False, idx=None):
    if idx is None:
        suffix = ""
    else: 
        suffix = "-" + str(idx)

    idx = (indic[:,0] == 0) * (indic[:,1] == 0)
    modes = [X[idx,:4], X[idx,4:]]
    alphas, _ = model[0].get_alpha_beta(modes)
    a = alphas.clone()
    idx = (indic[:,0] == 1) * (indic[:,1] == 0)
    modes = [X[idx,:4], X[idx,4:]]
    alphas, _ = model[0].get_alpha_beta(modes)
    b = alphas.clone()
    idx = (indic[:,0] == 0) * (indic[:,1] == 1)
    modes = [X[idx,:4], X[idx,4:]]
    alphas, _ = model[0].get_alpha_beta(modes)
    c = alphas.clone()
    barWidth = 0.25
    r1 = np.arange(3)
    r2 = [x + barWidth for x in r1]
    plt.figure() 
    plt.bar(r1, [torch.mean(a[:,0]).data.numpy(), torch.mean(b[:,0]).data.numpy(), torch.mean(c[:,0]).data.numpy()], width=barWidth, edgecolor='white', label=r'$\alpha$-ip')
    plt.bar(r2, [torch.mean(a[:,1]).data.numpy(), torch.mean(b[:,1]).data.numpy(), torch.mean(c[:,1]).data.numpy()], width=barWidth, edgecolor='white', label=r'$\alpha$-dm')
    plt.xticks([r + barWidth/2 for r in range(3)], ['uncorrupted', 'ip-noisy', 'dm-noisy'])
    for i, v in enumerate([torch.mean(a[:,0]).data.numpy(), torch.mean(b[:,0]).data.numpy(), torch.mean(c[:,0]).data.numpy()]):
        plt.text(i-0.07, v + .01, "%0.2f"%v, color='red', fontweight='bold', fontsize=21)
    for i, v in enumerate([torch.mean(a[:,1]).data.numpy(), torch.mean(b[:,1]).data.numpy(), torch.mean(c[:,1]).data.numpy()]):
        plt.text(i+0.17, v + .01, "%0.2f"%v, color='blue', fontweight='bold', fontsize=21)
    plt.legend(fontsize=19)
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.ylim([0, 1])
    if save: plt.savefig('results/noise-2/alpha-distrib' + suffix)
    plt.show()

    idx = (indic[:,0] == 0) * (indic[:,1] == 0)
    modes = [X[idx,:4], X[idx,4:]]
    _, betas = model[0].get_alpha_beta(modes)
    a = betas.clone()
    idx = (indic[:,0] == 1) * (indic[:,1] == 0)
    modes = [X[idx,:4], X[idx,4:]]
    _, betas = model[0].get_alpha_beta(modes)
    b = betas.clone()
    idx = (indic[:,0] == 0) * (indic[:,1] == 1)
    modes = [X[idx,:4], X[idx,4:]]
    _, betas = model[0].get_alpha_beta(modes)
    c = betas.clone()
    plt.figure()
    plt.bar(r1, [torch.mean(a[:,0]).data.numpy(), torch.mean(b[:,0]).data.numpy(), torch.mean(c[:,0]).data.numpy()], width=barWidth, edgecolor='white', label=r'$\beta$-ip')
    plt.bar(r2, [torch.mean(a[:,1]).data.numpy(), torch.mean(b[:,1]).data.numpy(), torch.mean(c[:,1]).data.numpy()], width=barWidth, edgecolor='white', label=r'$\beta$-dm')
    plt.xticks([r + barWidth/2 for r in range(3)], ['uncorrupted', 'ip-noisy', 'dm-noisy'])
    for i, v in enumerate([torch.mean(a[:,0]).data.numpy(), torch.mean(b[:,0]).data.numpy(), torch.mean(c[:,0]).data.numpy()]):
        plt.text(i-0.07, v + .01, "%0.2f"%v, color='red', fontweight='bold', fontsize=21)
    for i, v in enumerate([torch.mean(a[:,1]).data.numpy(), torch.mean(b[:,1]).data.numpy(), torch.mean(c[:,1]).data.numpy()]):
        plt.text(i+0.17, v + .01, "%0.2f"%v, color='blue', fontweight='bold', fontsize=21)
    plt.legend(fontsize=19)
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.ylim([0, 1])
    if save: plt.savefig('results/noise-2/beta-distrib' + suffix)
    plt.show()


# ---------------
def plot_yerkes_dodson(coldness, models, best_combo, X, y, save=False):
    f1 = []
    for tau in coldness:
        model = models['model-with'][(tau, best_combo[1], best_combo[2])]
        F1, _, recall, _ = evaluation(model, 'model-with', X, y)
        f1.append(F1)
    plt.plot(coldness, f1, marker='o')
    plt.xscale('log')
    plt.xlabel('coldness', fontsize=17)
    plt.ylabel('F1-score', fontsize=17)
    plt.ylim([0, 1])
    plt.tick_params(axis='both', which='major', labelsize=11)
    plt.legend(loc='upper left')
    if save: plt.savefig('results/yerkes-dodson')
    plt.show()


# ---------------
def plot_capacity_vs_coldness(coldness, models, best_combo, X, y, save=False):
    cap = []
    for tau in coldness:
        model = models['model-with'][(tau, best_combo[1], best_combo[2])]
        cap.append(model[0].capacity)
    plt.plot(coldness, cap, marker='o')
    plt.xscale('log')
    plt.xlabel('coldness', fontsize=17)
    plt.ylabel('capacity', fontsize=17)
    plt.ylim([0, 1])
    plt.tick_params(axis='both', which='major', labelsize=11)
    plt.legend(loc='upper left')
    if save: plt.savefig('results/capacity-vs-coldness')
    plt.show()


# ---------------
def plot_noise_generalisation(models, best_combo, X_test, y_test, save=False, idx=None):
    if idx is None:
        suffix = ""
    else: 
        suffix = "-" + str(idx)
    
    f1_with = []
    f1_without = []
    f1_base = []
    noises = np.linspace(0,2,50)
    beta_ip, beta_dm = [], []
    for noise in noises:
        X = torch.zeros(X_test.size()).float()
        X = X_test.clone()
        X[:,:4] = white_noise(X[:,:4].data.numpy(), noise)
        F1, _, recall, _ = evaluation(models['model-with'][best_combo], 'model-with', X, y_test)
        f1_with.append(F1)
        F1, _, recall, _ = evaluation(models['model-without'], 'model-without', X, y_test)
        f1_without.append(F1)
        F1, _, recall, _ = evaluation(models['base-model'], 'base-model', X, y_test)
        f1_base.append(F1)
        modes = [X[:,:4], X[:,4:]]
        _, betas = models['model-with'][best_combo][0].get_alpha_beta(modes)
        beta_ip.append(torch.mean(betas[:,0]).data.numpy())
        beta_dm.append(torch.mean(betas[:,1]).data.numpy())
    plt.plot(noises, f1_with, label='with')
    plt.plot(noises, f1_without, label='without')
    plt.plot(noises, f1_base, label='base')
    plt.axvline(x=0.5, ls='--', c='green')
    plt.xlabel(r'$\sigma$ corruption', fontsize=30)
    plt.ylabel('F1-score', fontsize=30)
    plt.ylim([0, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    if save: plt.savefig('results/noise-generalisation-ip-noisy' + suffix)
    plt.show()

    plt.plot(noises, beta_ip, label=r'$\beta$-ip')
    plt.plot(noises, beta_dm, label=r'$\beta$-dm')
    plt.xlabel(r'$\sigma$ corruption', fontsize=30)
    plt.ylabel(r'$\beta$', fontsize=30)
    plt.ylim([-0.1, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    if save: plt.savefig('results/noise-generalisation-ip-noisy-beta' + suffix)
    plt.show()


    beta_ip, beta_dm = [], []
    f1_with = []
    f1_without = []
    f1_base = []
    noises = np.linspace(0,2,50)
    for noise in noises:
        X = torch.zeros(X_test.size()).float()
        X = X_test.clone()
        X[:,4:] = white_noise(X[:,4:].data.numpy(), noise)
        F1, _, recall, _ = evaluation(models['model-with'][best_combo], 'model-with', X, y_test)
        f1_with.append(F1)
        F1, _, recall, _ = evaluation(models['model-without'], 'model-without', X, y_test)
        f1_without.append(F1)
        F1, _, recall, _ = evaluation(models['base-model'], 'base-model', X, y_test)
        f1_base.append(F1)
        modes = [X[:,:4], X[:,4:]]
        _, betas = models['model-with'][best_combo][0].get_alpha_beta(modes)
        beta_ip.append(torch.mean(betas[:,0]).data.numpy())
        beta_dm.append(torch.mean(betas[:,1]).data.numpy())
    plt.plot(noises, f1_with, label='with')
    plt.plot(noises, f1_without, label='without')
    plt.plot(noises, f1_base, label='base')
    plt.axvline(x=0.5, ls='--', c='green')
    plt.xlabel(r'$\sigma$ corruption', fontsize=30)
    plt.ylabel('F1-score', fontsize=30)
    plt.ylim([0, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    if save: plt.savefig('results/noise-generalisation-dm-noisy' + suffix)
    plt.show()

    plt.plot(noises, beta_ip, label=r'$\beta$-ip')
    plt.plot(noises, beta_dm, label=r'$\beta$-dm')
    plt.xlabel(r'$\sigma$ corruption', fontsize=30)
    plt.ylabel(r'$\beta$', fontsize=30)
    plt.ylim([-0.1, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    if save: plt.savefig('results/noise-generalisation-dm-noisy-beta' + suffix)
    plt.show()

    x = np.linspace(0,2,20)
    y = np.linspace(0,2,20)
    lx = len(x)
    ly =len(y)
    beta_ip, beta_dm = np.zeros((20,20)), np.zeros((20,20))

    for i in range(lx):
        noise_ip = x[i]
        X = X_test.clone()
        X[:,:4] = white_noise(X[:,:4].data.numpy(), noise_ip)
        for j in range(ly):
            noise_dm = y[j]
            X[:,4:] = white_noise(X[:,4:].data.numpy(), noise_dm)
            modes = [X[:,:4], X[:,4:]]
            _, betas = models['model-with'][best_combo][0].get_alpha_beta(modes)
            beta_ip[i,j] = torch.mean(betas[:,0]).data.numpy()
            beta_dm[i,j] = torch.mean(betas[:,1]).data.numpy()

    fig = plt.figure()
    ax = Axes3D(fig)
    ax = fig.gca(projection='3d')
    x, y = np.meshgrid(x, y)
    surf = ax.plot_surface(x, y, beta_ip, rstride=1, cstride=1, cmap='hot')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

    fig = plt.figure()
    ax = Axes3D(fig)
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x, y, beta_dm, rstride=1, cstride=1, cmap='hot')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()


# ---------------
def plot_specific(models, X_test, y_test, save=False):
    best_combo = (1e-4, 1e-2, 1e-3)
    f1_with = []
    f1_without = []
    f1_base = []
    noises = np.linspace(-20,5,50)
    beta_ip, beta_dm = [], []
    for noise in noises:
        X = torch.zeros(X_test.size()).float()
        X = X_test.clone()
        noise = 10**(noise/20)
        X[:,4:] = white_noise(X[:,4:].data.numpy(), noise)
        F1, _, recall, _ = evaluation(models['model-with'][best_combo], 'model-with', X, y_test)
        f1_with.append(F1)
        F1, _, recall, _ = evaluation(models['model-without'], 'model-without', X, y_test)
        f1_without.append(F1)
        F1, _, recall, _ = evaluation(models['base-model'], 'base-model', X, y_test)
        f1_base.append(F1)
        modes = [X[:,:4], X[:,4:]]
        _, betas = models['model-with'][best_combo][0].get_alpha_beta(modes)
        beta_ip.append(torch.mean(betas[:,0]).data.numpy())
        beta_dm.append(torch.mean(betas[:,1]).data.numpy())
    plt.plot(noises, f1_with, label='with', c='b')
    plt.plot(noises, f1_without, label='without')
    plt.plot(noises, f1_base, label='base')
    plt.axvline(x=20*np.log10(0.5), ls='--', c='darkgrey')
    plt.axhline(y=0.82, ls='--', c='grey')
    plt.xlabel('NSR (dB)', fontsize=30)
    plt.ylabel('F1-score', fontsize=30)
    plt.ylim([0, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    # plt.savefig('results/presentation/noise-generalisation-dm-noisy')
    plt.show()

    plt.plot(noises, beta_ip, label=r'$\beta$ corrupted mode', c='m')
    plt.plot(noises, beta_dm, label=r'$\beta$ other mode', c='orange')
    plt.xlabel('NSR (dB)', fontsize=30)
    plt.ylabel(r'$\beta$', fontsize=30)
    plt.ylim([-0.1, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    plt.savefig('results/presentation/noise-generalisation-dm-noisy-beta')
    plt.show()

    h_combo = (1e-4, 1e-2, 1e-1)
    m_combo = (1e-4, 1e-2, 1e-3)
    l_combo = (1e-4, 1e-2, 0)

    # h_combo = (1e-4, 1e-1, 1e-3)
    # m_combo = (1e-4, 1e-2, 1e-3)
    # l_combo = (1e-4, 0, 1e-3)

    # # h_combo = (1, 1e-2, 1e-3)
    # # m_combo = (1e-2, 1e-2, 1e-3)
    # # l_combo = (1e-4, 1e-2, 1e-3)

    f1_highcap = []
    f1_midcap = []
    f1_lowcap = []
    noises = np.linspace(-20,5,50)
    h_beta_ip, h_beta_dm = [], []
    m_beta_ip, m_beta_dm = [], []
    l_beta_ip, l_beta_dm = [], []
    for noise in noises:
        X = torch.zeros(X_test.size()).float()
        X = X_test.clone()
        noise = 10**(noise/20)
        X[:,:4] = white_noise(X[:,:4].data.numpy(), noise)
        F1, _, recall, _ = evaluation(models['model-with'][h_combo], 'model-with', X, y_test)
        f1_highcap.append(F1)
        F1, _, recall, _ = evaluation(models['model-with'][m_combo], 'model-with', X, y_test)
        f1_midcap.append(F1)
        F1, _, recall, _ = evaluation(models['model-with'][l_combo], 'model-with', X, y_test)
        f1_lowcap.append(F1)
        modes = [X[:,:4], X[:,4:]]

        _, betas = models['model-with'][h_combo][0].get_alpha_beta(modes)
        h_beta_ip.append(torch.mean(betas[:,0]).data.numpy())
        h_beta_dm.append(torch.mean(betas[:,1]).data.numpy())

        _, betas = models['model-with'][m_combo][0].get_alpha_beta(modes)
        m_beta_ip.append(torch.mean(betas[:,0]).data.numpy())
        m_beta_dm.append(torch.mean(betas[:,1]).data.numpy())

        _, betas = models['model-with'][l_combo][0].get_alpha_beta(modes)
        l_beta_ip.append(torch.mean(betas[:,0]).data.numpy())
        l_beta_dm.append(torch.mean(betas[:,1]).data.numpy())
    plt.plot(noises, f1_highcap, label='high energy regul.', c='purple')
    plt.plot(noises, f1_midcap, label='good energy regul.', c='b')
    plt.plot(noises, f1_lowcap, label='no energy regul.', c='skyblue')
    plt.axvline(x=20*np.log10(0.5), ls='--', c='darkgrey')
    plt.axhline(y=0.82, ls='--', c='grey')
    plt.xlabel('NSR (dB)', fontsize=30)
    plt.ylabel('F1-score', fontsize=30)
    plt.ylim([0, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    plt.savefig('results/presentation/energy-dm-noisy')
    plt.show()

    plt.plot(noises, h_beta_ip, label=r'$\beta$ corrupted mode', c='m')
    plt.plot(noises, h_beta_dm, label=r'$\beta$ other mode', c='orange')
    plt.axvline(x=20*np.log10(0.5), ls='--', c='darkgrey')
    plt.xlabel('NSR (dB)', fontsize=30)
    plt.ylabel(r'$\beta$', fontsize=30)
    plt.ylim([-0.1, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    plt.savefig('results/presentation/high-capacity-ip-noisy-beta')
    plt.show()

    plt.plot(noises, m_beta_ip, label=r'$\beta$ corrupted mode', c='m')
    plt.plot(noises, m_beta_dm, label=r'$\beta$ other mode', c='orange')
    plt.axvline(x=20*np.log10(0.5), ls='--', c='darkgrey')
    plt.xlabel('NSR (dB)', fontsize=30)
    plt.ylabel(r'$\beta$', fontsize=30)
    plt.ylim([-0.1, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    plt.savefig('results/presentation/normal-ip-noisy-beta')
    plt.show()

    plt.plot(noises, l_beta_ip, label=r'$\beta$ corrupted mode', c='m')
    plt.plot(noises, l_beta_dm, label=r'$\beta$ other mode', c='orange')
    plt.axvline(x=20*np.log10(0.5), ls='--', c='darkgrey')
    plt.xlabel('NSR (dB)', fontsize=30)
    plt.ylabel(r'$\beta$', fontsize=30)
    plt.ylim([-0.1, 1])
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc='best')
    plt.savefig('results/presentation/no-capacity-ip-noisy-beta')
    plt.show()


# ---------------
def plot_total_energy(models, best_combo, X_test, y_test, save=False):
    energy_system = []
    noises = np.linspace(0,2,50)
    f1 = []
    for noise in noises:
        X = torch.zeros(X_test.size()).float()
        bigmid = int(X.size(0)/2)
        smallmid = int(float(bigmid)/2)
        X = X_test.clone()
        X = white_noise(X.data.numpy(), noise)
        modes = [X[:,:4], X[:,4:]]
        energies = models['model-with'][best_combo][0].total_energy(modes).data.numpy()
        energy_system.append(np.mean(energies))
        F1, _, _, _ = evaluation(models['model-with'][best_combo], 'model-with', X, y_test)
        f1.append(F1)
    plt.plot(noises, energy_system)
    plt.xlabel(r'$\sigma$ corruption', fontsize=30)
    plt.ylabel('Total Energy', fontsize=30)
    plt.tick_params(axis='both', which='major', labelsize=25)
    if save: plt.savefig('results/noise-vs-system-energy')
    plt.show()

    plt.plot(noises, f1)
    plt.xlabel(r'$\sigma$ corruption', fontsize=30)
    plt.ylabel('F1-score', fontsize=30)
    plt.tick_params(axis='both', which='major', labelsize=25)
    if save: plt.savefig('results/noise-vs-system-f1')
    plt.show()


# ---------------
def plot_heatmap(models, meta, base_F1, cut_noise, X_test, y_test, save=False):
    X, y = torch.zeros(X_test.size()).float(), torch.zeros(y_test.size()).float()
    mid = int(X.size(0)/2)
    X[:mid, :4] = torch.tensor(white_noise(X_test[:mid, :4].data.numpy(), cut_noise)).float()
    X[mid:, 4:] = torch.tensor(white_noise(X_test[mid:, 4:].data.numpy(), cut_noise)).float()
    coldness = meta['coldness']
    lambda_regul = meta['lambda_regul']
    lambda_capacity = meta['lambda_capacity']
    score = np.zeros((len(lambda_regul),len(lambda_capacity)))
    for i, tau in enumerate(coldness):
        for j, l_cap in enumerate(lambda_capacity):
            best_F1 = -float("Inf")
            for l_reg in lambda_regul:
                F1, _, _, _ = evaluation(models['model-with'][(tau,l_reg,l_cap)], 'model-with', X, y_test)
                if F1 > best_F1:
                    best_F1 = F1
            score[i,j] = best_F1
    score = (score - base_F1)/base_F1
    ax = sns.heatmap(score, annot=True, xticklabels=lambda_capacity, yticklabels=coldness, cmap="YlGnBu")
    plt.xlabel('coldness', fontsize=17)
    plt.ylabel('lambda capacity', fontsize=17)
    if save: plt.savefig('results/heatmap')
    plt.show()


# ---------------
def print_evaluation(models, ranking, X, y, indic):
    print("F1-score -- Precision -- Recall -- Specificity")
    for name, model in models.items():
        print()
        print(name + ": ")
        if model is None: continue
        if name == 'model-with':
            for key in ranking:
                m = model[key]
                print(key)
                print("capacity: " + str(m[0].capacity.data.numpy()))
                m.eval()
                model_evaluation(m, name, X, y, indic)
            print()
        else:
            model.eval()
            model_evaluation(model, name, X, y, indic)
    print()

































