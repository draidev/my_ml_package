import os
import joblib
import pandas as pd
import numpy as np

#from sklearn.feature_selection import SelectFromModel
#from sklearn.ensemble import ek 
#from sklearn.model_selection import train_test_split
#from sklearn import tree, linear_model
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import category_encoders as ce

from ..data.malware_preprocess import extract_infos, preprocess_for_inference

class Model:
    def __init__(self, model_type='random_forest'):
        self.model = None
        self.model_type = None
        self.features = None
        self.df = None

        if model_type == 'random_forest':
            self.model = RandomForestClassifier()
            self.model_type = 'random_forest'

        if model_type == 'extra_trees':
            self.model = ek.ExtraTreesClassifier()
            self.model_type = 'extra_trees'

    def train(self, X, y):
        self.model.fit(X, y)
        
        
    ''' 
    def extratree_process(self, X, y, dataset):
        extratrees = ek.ExtraTreesClassifier().fit(X,y)
        model = SelectFromModel(extratrees, prefit=True, threshold=1.8e-2)
        X_new = model.transform(X)
        nbfeatures = X_new.shape[1]
        X_train, X_test, y_train, y_test = train_test_split(X_new, y ,test_size=0.2)
        self.features = list()
        index = np.argsort(extratrees.feature_importances_)[::-1][:nbfeatures]
        print("index : ", index)
        for f in range(nbfeatures):
            print("%d. feature %s (%f)" % (f + 1, dataset.columns[index[f]], extratrees.feature_importances_[index[f]]))
            self.features.append(dataset.columns[index[f]])

        model = { "DecisionTree":tree.DecisionTreeClassifier(max_depth=10),
             "RandomForest":ek.RandomForestClassifier(n_estimators=50),
             "Adaboost":ek.AdaBoostClassifier(n_estimators=50),
             "GradientBoosting":ek.GradientBoostingClassifier(n_estimators=50),
            }

        print("\n모델 성능 비교")
        # 모델 성능 비교
        results = {}
        for algo in model:
            clf = model[algo]
            clf.fit(X_train,y_train)
            score = clf.score(X_test,y_test)
            print ("%s : %s " %(algo, score))
            results[algo] = score
        
        return model[max(results, key=results.get)], self.features, results
    '''

    def predict(self, X_new):
        predictions = self.model.predict(X_new)
        return predictions


    def predict_proba(self, X_new):
        predict_probabilities = self.model.predict_proba(X_new)
        return predict_probabilities

    def inference_malware_file(self, file_path, pre_path=None):
        if isinstance(file_path, list):
            self.df = pd.DataFrame()
            index = 0
            for f in file_path:
                try:
                    data = extract_infos(f, inference=True)
                    data_df = self.dict_to_df(data)
                    #preprocessed_df = preprocess_for_inference(data_df, pre_path)
                    self.df = pd.concat([self.df, data_df], axis=0)
                except Exception as e:
                    i+=1
                    print(i, " Error: ", e)
                    pass
            return self.model.predict(self.df)

        else:
            data = extract_infos(file_path, inference=True)
            self.df = self.dict_to_df(data)
            #self.df = preprocess_for_inference(data_df, pre_path)
            return self.model.predict(self.df)


    def dict_to_df(self, dict_data):
        return pd.DataFrame.from_dict(dict_data, orient='index').T

    # inference with threshold parameter
    def get_predict_list_from_df(self, X_new, features=None, threshold=0.5):
        """
            if use ExtraTrees model then features variables set featurelist
        """

        if features != None:
            data = X_new.to_dict('records')
            pe_features = list()
            for d in data:
                pe_features.append(list(map(lambda x:d[x], features)))

            res = self.model.predict_proba(pe_features)
        else:
            data = X_new
            res = self.model.predict_proba(data)

        y_pred=list()
        for r in res:
            if r[1] > threshold:
                y_pred.append(1)
            else:
                y_pred.append(0)

        return y_pred


    def save_model(self, model_dir, model_name):
        try:
            full_path = os.path.join(model_dir, model_name)
            joblib.dump(self.model, full_path)
            print("save path :", full_path)
        except Exception as e:
            print("save model Error :", model_path)


    def load_model(self, model_path):
        try:
            with open(model_path, 'rb') as handle:
                self.model = joblib.load(handle)
                return self.model
        except Exception as e:
            print("load model Error :", model_path)
            
    ''' 
    def load_features(self, feature_path):
        try:
            self.features = pickle.loads((open(feature_path), 'rb').read())
        except Exception as e:
            print("load features Error :", e)
    '''
