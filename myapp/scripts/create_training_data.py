##**Machine Learning page related functions**##

from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question, Quiz_User
from myapp.scripts.cluster_input import ClusteringModelManager
import pandas as pd
import numpy as np
import uuid
import random
from sklearn.decomposition import PCA
import pickle

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.preprocessing import MinMaxScaler

## from myapp.scripts.create_training_data import create_data, silhouette, PCA_heatmap, percentile
## from importlib import reload
## import myapp.scripts.create_training_data as ctd

weighted_choices = {
        'beef': [0.2, 0.3, 0.4, 0.1],
        'lamb': [0.2, 0.1, 0.1, 0.6],
        'oth_meat': [0.2, 0.3, 0.4, 0.1],
        'car_type': [0.2, 0.2, 0.2, 0.1, 0.05, 0.02, 0.13, 0.1],
        'miles_driven': [0.1, 0.3, 0.4, 0.1, 0.1],
        'flights': [0.4, 0.15, 0.1, 0.05, 0.3],
        'home_electricity': [0.2, 0.8],
        'shopping': [0.3, 0.2, 0.2, 0.2, 0.1]
    }

#set number of clusters to test
range_n_clusters = [2, 3, 4, 5, 6]
# range_n_clusters = [2]

silhouette_paths = 'myapp/static/myapp/silhouette'
PCA_heatmap_path = 'myapp/static/myapp/PCA_heatmap.png'
model_path = 'myapp/ml_models/cluster_model.pkl'
heatmap_path = 'myapp/static/myapp/heatmap.png'
MinMaxScaler_path = 'myapp/ml_models/mmscaler.pkl' 

columns_to_drop = ['car_type','age','location']


#create training data
def create_data(n=1):

    for _ in range(n):
        user_id = uuid.uuid4()
        for question in Quiz_Question.objects.all():
            question_short = question.question_short
            choices = question.quiz_choice_set.all()
            chosen_choice = random.choices(choices,weights=weighted_choices.get(question_short))

            user, created = Quiz_User.objects.get_or_create(session_id=user_id)
            if created:
                user.save()
            response = Quiz_Response(session_id=user, question=question, choice=chosen_choice[0])
            response.save() 


#find optimal number of clusters
def silhouette():
    #get all data and preprocess
    my_cluster = ClusteringModelManager()
    X = my_cluster.get_cluster_data()

    X = pd.DataFrame(X)
    X = X.drop(columns=columns_to_drop) 
    X = X.reset_index(drop=True) 
    mmscaler = MinMaxScaler()
    X = mmscaler.fit_transform(X)

    #create charts
    for n_clusters in range_n_clusters:
        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(7, 7)

        ax.set_xlim([-0.1, 1])
        ax.set_ylim([0, len(X) + (n_clusters + 1) * 10])

        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(X)
        
         # The silhouette_score gives the average value for all the samples
        silhouette_avg = silhouette_score(X, cluster_labels)
        print(
            "For n_clusters =",
            n_clusters,
            "The average silhouette_score is :",
            silhouette_avg,
        )

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(X, cluster_labels)

        y_lower = 10
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax.fill_betweenx(
                np.arange(y_lower, y_upper),
                0,
                ith_cluster_silhouette_values,
                facecolor=color,
                edgecolor=color,
                alpha=0.7,
            )

            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
            y_lower = y_upper + 10 

        ax.set_title(f"The silhouette plot for the {n_clusters} clusters.")
        ax.set_xlabel("The silhouette coefficient values")
        ax.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax.set_yticks([])  # Clear the yaxis labels / ticks
        ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        plt.savefig(silhouette_paths + str(n_clusters) + '.png')


#run/save model and scaler, interpret/validation after picking num of clusters
def PCA_heatmap(n_clusters=4):
    my_cluster = ClusteringModelManager()
    X = my_cluster.get_cluster_data()

    X = pd.DataFrame(X)
    X = X.drop(columns=columns_to_drop) 
    X = X.reset_index(drop=True) 
    mmscaler = MinMaxScaler()
    X_input = mmscaler.fit_transform(X)
    #save scaler
    with open(MinMaxScaler_path,'wb') as file:
            pickle.dump(mmscaler,file)

    kmeans = KMeans(n_clusters=n_clusters,random_state=0)
    cluster_labels = kmeans.fit_predict(X_input)
    X['cluster_label'] = cluster_labels

    #save ml model locally for loading in view later
    filename = model_path
    with open(filename,'wb') as file:
        pickle.dump(kmeans,file)
    
    #separate heatmap
    averages = X.groupby('cluster_label').mean()
    averages_scaled = MinMaxScaler().fit_transform(averages)
    plt.figure(figsize=(10, 6))
    sns.heatmap(averages_scaled, annot=True, xticklabels=averages.columns.tolist() ,cmap='GnBu')
    plt.xticks(rotation=45)
    plt.title("Heatmap showing impact of each feature within cluster", loc='center')
    plt.xlabel("Feature")
    plt.ylabel("Cluster")
    plt.subplots_adjust(bottom=0.3) 
    plt.savefig(heatmap_path)
    plt.close()

    #CREATE CHARTS
    fig, (ax1, ax2) = plt.subplots(1,2, width_ratios=[2,1])
    fig.set_size_inches(20, 7)

    #HEATMAP
    sns.heatmap(averages_scaled, annot=True, xticklabels=averages.columns.tolist() ,cmap='GnBu', ax=ax1)
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.set_title("Heatmap showing impact of each feature within cluster")
    ax1.set_xlabel("Feature")
    ax1.set_ylabel("Cluster")

    #PCA
    colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
    pca = PCA(n_components=2)
    X_PCA = pca.fit_transform(X_input)
    ax2.scatter(
        X_PCA[:, 0], X_PCA[:, 1], marker=".", s=30, lw=0, alpha=0.7, c=colors, edgecolor="k"
    )

    #Labeling the clusters
    centers = kmeans.cluster_centers_
    centers_PCA = pca.transform(centers)
    # Draw white circles at cluster centers
    ax2.scatter(
        centers_PCA[:, 0],
        centers_PCA[:, 1],
        marker="o",
        c="white",
        alpha=1,
        s=200,
        edgecolor="k",
    )

    for i, c in enumerate(centers_PCA):
        ax2.scatter(c[0], c[1], marker="$%d$" % i, alpha=1, s=50, edgecolor="k")

    ax2.set_title("The visualization of the clustered data after PCA to 2 dimensions")
    ax2.set_xlabel("Feature space for the 1st feature")
    ax2.set_ylabel("Feature space for the 2nd feature")

    plt.suptitle(
        "PCA for KMeans clustering on sample data with n_clusters = %d"
        % n_clusters,
        fontsize=14,
        fontweight="bold",
    )

    plt.subplots_adjust(bottom=0.2) 
    plt.savefig(PCA_heatmap_path)
    # print(pca.components_)
    print(f'Explained variance Ratio: {pca.explained_variance_ratio_}')

    

