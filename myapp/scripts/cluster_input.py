from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question
import pandas as pd

# result = {}
# for response in Quiz_Response.objects:
#     question_id = response['question']
#     choice_id = response['choice']

#     choice_obj = Quiz_Choice.objects.get(pk=choice_id)
#     emission = choice_obj['choice_num'] * choice_obj['assumption'] * choice_obj['scale'] * choice_obj['emission_factor']

#     question_obj = Quiz_Question.objects.get(pk=question_id)
#     question_short_name = question_obj['question_short']

#     if question_short_name not in result.keys:
#         result[question_short_name] = emission


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
    

