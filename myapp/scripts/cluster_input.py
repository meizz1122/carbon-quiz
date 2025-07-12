##**User cluster results related methods**##

from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question, Quiz_User
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, Normalizer
import pickle

import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import matplotlib.pyplot as plt

## python manage.py shell
## from myapp.scripts.cluster_input import ClusteringModelManager
## my_cluster = ClusteringModelManager()
## my_cluster.get_emission('1ce97cab-bf74-40bb-a9fd-24d86affafef')

class ClusteringModelManager:
    def __init__(self):
        #TODO post deployment (GCP, Heroku etc) use self.model_path = os.path.join(settings.BASE_DIR, 'scripts', 'saved_model.pkl')
        self.model_path = 'myapp/ml_models/cluster_model.pkl' # static path
        self.heatmap_path = 'myapp/static/myapp/heatmap.png' # static path
        self.MinMaxScaler_path = 'myapp/ml_models/mmscaler.pkl' # static path
        self.model = None
        self.cluster_labels = None
        self.df = None
        self.columns_to_drop = ['car_type','age','location']


    #preprocess input data for model, retrieve all responses in database and pivot into one column per feature 
    #don't need self for static functions vs instance method
    def get_cluster_data(self):
        responses = Quiz_Response.objects.select_related('session_id', 'question', 'choice')

        data = [
            {
                'session_id': r.session_id,
                'question_short_name': r.question.question_short,
                'emission': r.choice.choice_num * r.choice.assumption * r.choice.scale * r.choice.emission_factor
            }
            #r is a response object; r.question returns related question object/instance
            for r in responses
        ]

        df = pd.DataFrame(data)
        df_pivot = pd.pivot(df, index='session_id', columns='question_short_name', values='emission')

        return df_pivot


    #retrieve single user data
    def get_user_data(self, session_id):
        # retrieve choices, sum, save to model?, return
        responses = Quiz_Response.objects.filter(session_id=session_id).select_related('session_id', 'question', 'choice')

        data = [
            {
                'session_id': r.session_id,
                'question_short_name': r.question.question_short,
                'emission': r.choice.choice_num * r.choice.assumption * r.choice.scale * r.choice.emission_factor
            }
            #r is a response object; r.question returns related question object/instance
            for r in responses
        ]

        df = pd.DataFrame(data)
        df = pd.pivot(df, index='session_id', columns='question_short_name', values='emission')
        return df
    

    #NOTE only for INDIVIDUAL user data, loads previously created minmaxscaler from train_model()
    def preprocess_user_data(self, df):
        #preprocess: remove session_id as first column, normalize
        df = pd.DataFrame(df)
        df = df.drop(columns=self.columns_to_drop) 
        df_input = df.reset_index(drop=True)
        
        with open(self.MinMaxScaler_path, 'rb') as file:
            loaded_scaler = pickle.load(file)
        
        df_input = loaded_scaler.transform(df_input)

        return df_input
    

    #not necessary to calc total emission during model training?! only need to calc/retrieve the current active user
    def get_user_emission(self, session_id):
        df = self.get_user_data(session_id=session_id)
        df = df.drop(columns=self.columns_to_drop)
        sum = df.sum(axis=1).iloc[0]
        return round(sum)


    def get_user_cluster(self, session_id):
        # load, predict, save to model? return
        filename = self.model_path
        with open(filename, 'rb') as file:
            loaded_model = pickle.load(file)

        user_data = self.get_user_data(session_id=session_id)
        processed_data = self.preprocess_user_data(df=user_data)

        user_cluster = loaded_model.predict(processed_data)

        return user_cluster[0]