from StudentSupport.models import *


def serialize_feedback(feedback_qs, faculty_obj, semester_list):
    # feedback_distinct = feedback_qs.filter()
    subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=faculty_obj, subject_id__semester__in=semester_list)
    ratings = []
    for i in subject_qs:
        tmp = {
            'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0, 'Q5': 0,
            'Q6': 0, 'Q7': 0, 'Q8': 0, 'Q9': 0, 'Q10': 0,
        }
        print(i.subject_id.id, i.subject_id.subject_name)
        tmp['subject_id'] = i.subject_id.id
        tmp['subject_name'] = i.subject_id.subject_name
        feedback_distinct = feedback_qs.filter(subject_id_id=i.subject_id.id)
        div = feedback_distinct.count()
        if div > 0:
            for j in feedback_distinct:
                # getting sum of all the feedback.
                tmp['Q1'] += j.Q1
                tmp['Q2'] += j.Q2
                tmp['Q3'] += j.Q3
                tmp['Q4'] += j.Q4
                tmp['Q5'] += j.Q5
                tmp['Q6'] += j.Q6
                tmp['Q7'] += j.Q7
                tmp['Q8'] += j.Q8
                tmp['Q9'] += j.Q9
                tmp['Q10'] += j.Q10

            # calculating average of all the feedback
            tmp['Q1'] = tmp['Q1'] / div
            tmp['Q2'] = tmp['Q2'] / div
            tmp['Q3'] = tmp['Q3'] / div
            tmp['Q4'] = tmp['Q4'] / div
            tmp['Q5'] = tmp['Q5'] / div
            tmp['Q6'] = tmp['Q6'] / div
            tmp['Q7'] = tmp['Q7'] / div
            tmp['Q8'] = tmp['Q8'] / div
            tmp['Q9'] = tmp['Q9'] / div
            tmp['Q10'] = tmp['Q10'] / div

        else:
            # It is for that subjects whose feedback has not been submitted yet.
            pass

        # appending tmp dictionary into rating list
        ratings.append(tmp)

    # Returning ratings object
    return ratings
