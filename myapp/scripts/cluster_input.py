from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question, Quiz_User
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, Normalizer
import pickle
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
    def preprocess_data(self, df):
        #preprocess: remove session_id as first column, normalize
        df = pd.DataFrame(df)
        df = df.drop(columns=['car_type','age','location']) #NOTE update here and in train_model()
        df_input = df.reset_index(drop=True)
        
        with open(self.MinMaxScaler_path, 'rb') as file:
            loaded_scaler = pickle.load(file)
        
        df_input = loaded_scaler.transform(df_input)

        return df_input


    #train and save model locally, storing user labels back to Quiz_User
    def train_model(self):
        #preprocess
        df = self.get_cluster_data()
        df = pd.DataFrame(df)
        df = df.drop(columns=['car_type','age','location']) #NOTE update here and in preprocess_data()

        #total by session_id
        total = df.sum(axis=1)

        #create and save scaler
        df_input = df.reset_index(drop=True) #drop session_ids now
        mmscaler = MinMaxScaler()
        df_input = mmscaler.fit_transform(df_input)
        with open(self.MinMaxScaler_path,'wb') as file:
            pickle.dump(mmscaler,file)

        # train model
        kmeans = KMeans(n_clusters=4,random_state=0)
        cluster_labels = kmeans.fit_predict(df_input)

        df['cluster_label'] = cluster_labels
        df['total_emission'] = total
        # print(df.head)

        # # NOT necessary?? save labels to Quiz_User model; 
        # # TODO apparently iterrows() is very slow..suggestion later to use bulk_update
        # for index, row in df.iterrows():
        #     try:
        #         # print(df.columns.tolist())
        #         # print(df.index.name)
        #         print()
        #         user = Quiz_User.objects.get(pk=row.name)
        #         user.cluster_label = int(row['cluster_label'])
        #         user.total_emission = round(row['total_emission'])
        #         user.save()
        #         print(f"User {row.name} found and updated")
        #     except Quiz_User.DoesNotExist:
        #         print(f"User {row.name} not found.")
        
        #save ml model locally for loading in view later
        filename = self.model_path
        with open(filename,'wb') as file:
            pickle.dump(kmeans,file)

        #create and save heatmap 
        df = df.drop(columns=['total_emission'])
        averages = df.groupby('cluster_label').mean()
        # print(averages)
        averages_scaled = MinMaxScaler().fit_transform(averages)
        sns.heatmap(averages_scaled, annot=True, xticklabels=averages.columns.tolist() ,cmap='GnBu')
        plt.xticks(rotation=45)
        plt.xlabel("Feature")
        plt.ylabel("Cluster")
        plt.rcParams["figure.figsize"] = (6,11)
        plt.subplots_adjust(bottom=0.3) 
        # plt.show()
        plt.savefig(self.heatmap_path)


    #not necessary to calc total emission during model training?! only need to calc/retrieve the current active user
    def get_emission(self, session_id):
        df = self.get_user_data(session_id=session_id)
        df = df.drop(columns=['car_type'])
        sum = df.sum(axis=1).iloc[0]
        return round(sum)


    def get_cluster(self, session_id):
        # load, predict, save to model? return
        filename = self.model_path
        with open(filename, 'rb') as file:
            loaded_model = pickle.load(file)

        user_data = self.get_user_data(session_id=session_id)
        processed_data = self.preprocess_data(df=user_data)

        user_cluster = loaded_model.predict(processed_data)

        return user_cluster[0]

