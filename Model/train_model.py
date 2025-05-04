import numpy as np
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree, ensemble
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score


train_df = pd.read_csv('cStick.csv')
train_df= train_df.drop(['Distance', 'Pressure', 'Sugar level'], axis=1)

outcome_dict = {0:'No Fall detected',1:'Slip detected',2:'Definite fall'}
outcome_list = ['No Fall detected','Slip detected','Definite fall']

feature_list = [ 'HRV', 'SpO2', 'Accelerometer']

train_df_all_cols = train_df.columns

train_df1 = train_df.astype(float)

C = train_df1.to_numpy()

features = C[:,0:3]
labels = C[:,-1]

indices = np.random.permutation(len(labels)) 

X = features[indices]
y = labels[indices]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) 

depth =1
num_trees = 4


clf = ensemble.RandomForestClassifier(max_depth = depth, n_estimators = num_trees, max_samples = 0.5)

clf.fit(X_train,y_train)

best_d = 1         # range(1,6)
best_ntrees = 1   # [50,150,250]
best_accuracy = 0

for d in range(1,6):
    for n_trees in [2,3,4]:
        clf = ensemble.RandomForestClassifier(max_depth=d,n_estimators=n_trees,max_samples=0.5)
        cv_scores = cross_val_score(clf,X_train,y_train,cv=5) # 5 means 80/20 split
        average_cv_accuracy =cv_scores.mean()
        
        if average_cv_accuracy>best_accuracy:
            best_accuracy = average_cv_accuracy
            best_d = d
            best_ntrees = n_trees

best_depth = best_d
best_num_trees = best_ntrees

clf_validated = ensemble.RandomForestClassifier(max_depth = best_depth, n_estimators = best_num_trees, max_samples = 0.5)

clf_validated.fit(X_train,y_train)

with open('fall_detection_model.pkl', 'wb') as f:
    pickle.dump(clf_validated, f)

print("Model trained and saved to 'fall_detection_model.pkl'")