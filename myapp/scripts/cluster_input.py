from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question, Quiz_User
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

## python manage.py shell
## from myapp.scripts.cluster_input import get_cluster_data, train_model
# df = get_cluster_data()
# train_model(df)

#preprocess input data for model, retrieve user data from database
def get_cluster_data():
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

#train and save model locally, storing user labels back to Quiz_User
def train_model(df):
    #preprocess: remove session_id as first column, normalize
    df = pd.DataFrame(df)
    df = df.drop(columns=['car_type'])

    total = df.sum(axis=1)

    df_input = df.reset_index(drop=True)
    df_input = MinMaxScaler().fit_transform(df_input)

    # train model
    kmeans = KMeans(n_clusters=4,random_state=0)
    cluster_labels = kmeans.fit_predict(df_input)

    df['cluster_label'] = cluster_labels
    df['total_emission'] = total
    # print(df.head)

    # save labels to Quiz_User model; TODO apparently iterrows() is very slow..suggestion later to use bulk_update
    for index, row in df.iterrows():
        try:
            # print(df.columns.tolist())
            # print(df.index.name)
            print()
            user = Quiz_User.objects.get(pk=row.name)
            user.cluster_label = int(row['cluster_label'])
            user.total_emission = int(row['total_emission'])
            user.save()
            print(f"User {row.name} found and updated")
        except Quiz_User.DoesNotExist:
            print(f"User {row.name} not found.")
    
    #save ml model locally for loading in view later
    filename = 'myapp/ml_models/cluster_model.pkl'
    with open(filename,'wb') as file:
        pickle.dump(kmeans,file)

# # TODO
# #not necessary to calc total emission during model training?! only need to calc/retrieve the current active user
# def get_emission(session_id):

# def get_cluster(session_id):

## save heatmap locally to later pass into template
# def get_heatmap():
#     averages = df.groupby('cluster_label').mean()
#     # print(averages)
#     averages_scaled = MinMaxScaler().fit_transform(averages)
#     sns.heatmap(averages_scaled, annot=True, xticklabels=averages.columns.tolist() ,cmap='GnBu')
#     plt.xticks(rotation=45)
#     plt.xlabel("Feature")
#     plt.ylabel("Cluster")
#     plt.show()
