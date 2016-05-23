import datetime
import numpy as np
import pickle
import scipy.io
import sklearn.decomposition
import sklearn.ensemble
import sklearn.metrics
import sklearn.preprocessing

np.set_printoptions(precision=2)

method = 'joint'

# Load
mat = scipy.io.loadmat("mdb" + method + ".mat")
data = mat["mdb" + method + "_data"]

X_training = data["X_training"][0][0]
X_validation = data["X_validation"][0][0]
X_test = data["X_test"][0][0]

Y_training = np.ravel(data["Y_training"][0][0])
Y_validation = np.ravel(data["Y_validation"][0][0])
Y_test = np.ravel(data["Y_test"][0][0])

X_training = np.concatenate((X_training, X_validation))
Y_training = np.concatenate((Y_training, Y_validation))

# Discard features with less than 10% of the energy
energies = X_training * X_training
feature_energies = np.mean(X_training, axis=0)
feature_energies /= np.sum(feature_energies)
sorting_indices = np.argsort(feature_energies)
sorted_feature_energies = feature_energies[sorting_indices]
cumulative = np.cumsum(sorted_feature_energies)
start_feature = np.where(cumulative > 0.1)[0][0]
dominant_indices = sorting_indices[start_feature:]

X_training = X_training[:, dominant_indices]
X_validation = X_validation[:, dominant_indices]
X_test = X_test[:, dominant_indices]

n_examples, n_features = X_training.shape
toleration = 1e-3
den = np.zeros(n_features)
for feature_id in range(n_features):
    feature = X_training[:, feature_id]
    lower_bound = np.finfo(float).eps
    if scipy.stats.skew(np.log(lower_bound + feature)) > 0.0:
        X_training[:, feature_id] = np.log(lower_bound + feature)
        X_test[:, feature_id] = np.log(lower_bound + X_test[:, feature_id])
    else:
        upper_bound = np.median(feature)
        midpoint = 0.5 * (lower_bound + upper_bound)
        skewness = scipy.stats.skew(np.log1p(feature / midpoint))
        while abs(skewness) > toleration:
            if skewness > 0.0:
                upper_bound = midpoint
            elif skewness < 0.0:
                lower_bound = midpoint
            midpoint = 0.5 * (lower_bound + upper_bound)
            skewness = scipy.stats.skew(np.log1p(feature / midpoint))
        den[feature_id] = midpoint / np.median(feature)
        X_training[:, feature_id] = np.log1p(feature / midpoint)
        X_test[:, feature_id] = np.log1p(X_test[:, feature_id] / midpoint)



# Standardize features
scaler = sklearn.preprocessing.StandardScaler().fit(X_training)
X_training = scaler.transform(X_training)
X_test = scaler.transform(X_test)


report = []
output_file = open('mdb' + method + 'svm_y.pkl', 'wb')
pickle.dump(report, output_file)
output_file.close()

for C in [1e6, 1e8, 1e10]:
    for gamma in [0.5]:
        print(C, gamma)
        print datetime.datetime.now().time()
        clf = sklearn.svm.SVC(C=C, gamma=gamma, class_weight="balanced")
        clf.fit(X_training, Y_training)
        Y_training_predicted = clf.predict(X_training)
        Y_test_predicted = clf.predict(X_test)
        dictionary = {'C': C,
            'Y_test': Y_test,
            'Y_test_predicted': Y_test_predicted,
            'Y_training': Y_training,
            'Y_training_predicted': Y_training_predicted}
        Y_training = dictionary["Y_training"]
        Y_training_predicted = dictionary["Y_training_predicted"]
        Y_test = dictionary["Y_test"]
        Y_test_predicted = dictionary["Y_test_predicted"]
        #print(sklearn.metrics.classification_report(Y_training, Y_training_predicted))
        print(sklearn.metrics.classification_report(Y_test, Y_test_predicted))
