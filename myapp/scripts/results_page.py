from myapp.scripts.cluster_input import ClusteringModelManager
from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question, Quiz_User
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
from math import ceil
import os
from django.conf import settings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
import tempfile

percentile_path = os.path.join(tempfile.gettempdir(), 'percentile.png') 
subgroups_path =  os.path.join(tempfile.gettempdir(), 'subgroups.png') 
user_top5_path = os.path.join(tempfile.gettempdir(), 'top5.png') 

columns_to_drop = ['car_type','age','location']


def generate_percentile_grade(session_id=None):
    my_cluster = ClusteringModelManager()
    
    #group data
    X = my_cluster.get_cluster_data()
    X = X.drop(columns=columns_to_drop) 
    total_emissions = X.sum(axis=1)
    p = [0, 25, 50, 75, 100]
    percentiles = np.percentile(total_emissions, p)

    #user specific data
    user_data = my_cluster.get_user_data(session_id=session_id)
    user_total_emissions = user_data.sum(axis=1).values
    user_percentile = percentileofscore(a=total_emissions,score=user_total_emissions)
    
    grades = ['FANTASTIC', 'GREAT', 'GOOD', 'OK']
    user_grade = ''
    for i, percentile_value in enumerate(percentiles[1:]):
        if user_total_emissions <= percentile_value:
            user_grade = grades[i]
            break

    #create chart
    fig, ax = plt.subplots(figsize=(8, 5))

    widths = [percentiles[i+1] - percentiles[i] for i in range(len(percentiles)-1)]  
    colors = ["#52d284", "#9fde84", "#feb05a", "#fa5e46"]  

    left = percentiles[0]
    for width, color in zip(widths, colors):
        ax.barh(y=0, width=width, left=left, height=0.5, color=color, edgecolor=None)
        left += width

    ax.axvline(x=percentiles[2], color="#343434", linestyle="--")
    ax.text(x=percentiles[2],y=-0.31, s='Median', ha='center', va='bottom',fontfamily='Verdana', color='#343434', fontsize=10)

    ax.axvline(x=user_total_emissions, color="black", linestyle="--", linewidth=2.5)
    ax.text(x=user_total_emissions,y=-0.35, s='You', ha='center', fontfamily='Verdana', color='black', fontweight='bold', fontsize=12)

    ax.text(x=percentiles[0],y=-0.26, s='Low Impact', ha='left', va='top', fontfamily='Verdana', color='#52d284', fontweight='light', fontsize=10)
    ax.text(x=percentiles[-1],y=-0.26, s='High Impact', ha='right',va='top', fontfamily='Verdana', color='#fa5e46', fontweight='light', fontsize=10)

    ax.set_title("Your Total Emissions Compared to Population Quartiles", fontsize=14, color='#343434')
    ax.set_xlim(0, percentiles[-1])
    ax.axis('off')

    plt.figtext(0.05, 0.9, s=f"You're doing ", fontfamily='Verdana', color='#343434', fontweight='normal', fontsize=22)
    plt.figtext(0.3, 0.9, s=f"{user_grade}!", fontfamily='Verdana', color='#343434', fontweight='bold', fontsize=23)
    plt.figtext(0.05, 0.05, s=f"You scored better than ", fontfamily='Verdana', color='#343434', fontweight='normal', fontsize=22)
    plt.figtext(0.50, 0.05, s=f"{int(100 - user_percentile)}%", fontfamily='Verdana', color='#343434', fontweight='bold', fontsize=23)
    plt.figtext(0.63, 0.05, s=f"of users", fontfamily='Verdana', color='#343434', fontweight='normal', fontsize=22)

    plt.subplots_adjust(top=0.75, bottom=0.25) 
    plt.savefig(percentile_path)
    plt.close()

    return user_percentile, user_grade


def generate_similar_subgroup(session_id=None):
    my_cluster = ClusteringModelManager()
    X = my_cluster.get_cluster_data()
    user_data = my_cluster.get_user_data(session_id=session_id)
    user_data = user_data.reset_index(drop=True) 
    user_emission = my_cluster.get_user_emission(session_id=session_id)

    #user group
    user_age = user_data.loc[0, 'age']
    user_geo = user_data.loc[0 ,'location']

    #group averages
    age_avg_data = X.drop(columns=['car_type', 'location'])
    age_mask = age_avg_data['age'] == user_age
    age_avg = age_avg_data[age_mask].sum(axis=1).mean()

    geo_avg_data = X.drop(columns=['car_type', 'age'])
    geo_mask = geo_avg_data['location'] == user_geo
    geo_avg = geo_avg_data[geo_mask].sum(axis=1).mean()

    age_diff = f"{ceil((user_emission - age_avg)/age_avg *100):+}%"
    geo_diff = f"{ceil((user_emission - geo_avg)/geo_avg *100):+}%"

    #charting
    labels = ['Age \n Group', 'Location/ \n Geography']
    chart_data = {
    'You': (user_emission, user_emission),
    'Group Avg': (int(age_avg), int(geo_avg))
    }
    bar_colors = ["#45b5c3", "#D3D3D3"]
    bar_labels = [[f'You ({age_diff})', f'You ({geo_diff})'], [' Group \n Avg',' Group \n Avg']]
    bar_label_weights = ['bold', 'normal']

    x = np.array([0, 0.8])  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots()

    for i, key in enumerate(chart_data):
        offset = width * multiplier
        rects = ax.barh(x + offset, chart_data.get(key), width, label=key, color=bar_colors[i])
        ax.bar_label(rects, labels=bar_labels[i], color='#343434', weight=bar_label_weights[i])
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_yticks(x + width - 0.125, labels, color='#343434')
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False) 
    # ax.spines['left'].set_visible(False)
    plt.subplots_adjust(top=0.75, left=0.2) 

    plt.figtext(0.05, 0.9, s=f"Here's how you ", fontfamily='Verdana', color='#343434', fontweight='normal', fontsize=18)
    plt.figtext(0.37, 0.9, s=f"compare", fontfamily='Verdana', color='#45b5c3', fontweight='bold', fontsize=19)
    plt.figtext(0.05, 0.83, s=f"Within similar subgroups", fontfamily='Verdana', color='#343434', fontweight='normal', fontsize=12)

    plt.savefig(subgroups_path)
    plt.close()


def generate_user_categories(session_id=None):
    my_cluster = ClusteringModelManager()
    user_data = my_cluster.get_user_data(session_id=session_id)
    user_data = user_data.drop(columns=columns_to_drop) 
    user_data = user_data.reset_index(drop=True) 

    row1 = user_data.iloc[0]
    row1 = row1.sort_values(ascending=False)
    top_5 = row1[:5]
    top_5['other'] = row1[5:].sum()
    
    colors = ['#F66D44', '#FEAE65', '#E6F69D', '#AADEA7', '#64C2A6', '#2D87BB']

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(top_5, labels=top_5.index.tolist(), autopct='%1.0f%%', colors=colors, textprops={'color': '#343434', 'fontfamily':'Verdana'})
    ax.set_title('Your top 5 categories with the most impact', fontfamily='Verdana', color='#343434', ha='center', fontsize=15, fontweight='demibold')
    plt.subplots_adjust(bottom=0.02, left=0.1, right=0.9) 
    plt.tight_layout()
    plt.savefig(user_top5_path, facecolor="#f6f6f6", edgecolor='none')
    plt.close()


def recommended_actions(session_id=None):
    my_cluster = ClusteringModelManager()
    user_data = my_cluster.get_user_data(session_id=session_id)
    user_data = user_data.drop(columns=columns_to_drop) 
    user_data = user_data.reset_index(drop=True) 

    user_total_emissions = user_data.sum(axis=1).values

    if user_total_emissions == 0:
        user_total_emissions = 1

    row1 = user_data.iloc[0]
    row1 = row1.sort_values(ascending=False)
    top_5 = row1[:5]
    labels=top_5.index.tolist()

    special_recs = ['beef', 'lamb', 'oth_meat', 'dairy', 'flights']
    results = []

    for label in labels:
        cat_emission = top_5.loc[label]
        if cat_emission != 0:
            Question = Quiz_Question.objects.get(question_short=label)
            rec = Question.recommended_action
            if label in special_recs:
                Response= Quiz_Response.objects.get(session_id=session_id, question=Question.pk)
                Choice = Response.choice
                choice_num = Choice.choice_num
                percent = ceil(cat_emission/choice_num/user_total_emissions*100)
                results.append(f"{rec} {int(percent)}%")
            else:
                results.append(rec)
        else:
            break
            
    return(results)



