from StudentSupport.models import *


# Function for getting question wise average feedback for all subject of perticular faculty.
def serialize_feedback(feedback_qs, faculty_obj, semester_list):
    # feedback_distinct = feedback_qs.filter()
    subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=faculty_obj,
                                                           subject_id__semester__in=semester_list)
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
            tmp['Q1'] = round((tmp['Q1'] / div), 2)
            tmp['Q2'] = round((tmp['Q2'] / div), 2)
            tmp['Q3'] = round((tmp['Q3'] / div), 2)
            tmp['Q4'] = round((tmp['Q4'] / div), 2)
            tmp['Q5'] = round((tmp['Q5'] / div), 2)
            tmp['Q6'] = round((tmp['Q6'] / div), 2)
            tmp['Q7'] = round((tmp['Q7'] / div), 2)
            tmp['Q8'] = round((tmp['Q8'] / div), 2)
            tmp['Q9'] = round((tmp['Q9'] / div), 2)
            tmp['Q10'] = round((tmp['Q10'] / div), 2)
            tmp['count'] = div

        else:
            # It is for that subjects whose feedback has not been submitted yet.
            tmp['count'] = div
            pass

        # appending tmp dictionary into rating list
        ratings.append(tmp)

    # Returning ratings object
    return ratings


# This function is for perticular subject of faculty
# Feedback Queryset has been given already.
def serialize_feedback_subject(feedback_qs):
    rating_dict = {
        'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0, 'Q5': 0,
        'Q6': 0, 'Q7': 0, 'Q8': 0, 'Q9': 0, 'Q10': 0,
    }
    divisor = feedback_qs.count()
    rating_dict['count'] = divisor
    if divisor > 0:
        for j in feedback_qs:
            # getting sum of all the feedback.
            rating_dict['Q1'] += j.Q1
            rating_dict['Q2'] += j.Q2
            rating_dict['Q3'] += j.Q3
            rating_dict['Q4'] += j.Q4
            rating_dict['Q5'] += j.Q5
            rating_dict['Q6'] += j.Q6
            rating_dict['Q7'] += j.Q7
            rating_dict['Q8'] += j.Q8
            rating_dict['Q9'] += j.Q9
            rating_dict['Q10'] += j.Q10

        # calculating average of all the feedback
        rating_dict['Q1'] = round((rating_dict['Q1'] / divisor), 2)
        rating_dict['Q2'] = round((rating_dict['Q2'] / divisor), 2)
        rating_dict['Q3'] = round((rating_dict['Q3'] / divisor), 2)
        rating_dict['Q4'] = round((rating_dict['Q4'] / divisor), 2)
        rating_dict['Q5'] = round((rating_dict['Q5'] / divisor), 2)
        rating_dict['Q6'] = round((rating_dict['Q6'] / divisor), 2)
        rating_dict['Q7'] = round((rating_dict['Q7'] / divisor), 2)
        rating_dict['Q8'] = round((rating_dict['Q8'] / divisor), 2)
        rating_dict['Q9'] = round((rating_dict['Q9'] / divisor), 2)
        rating_dict['Q10'] = round((rating_dict['Q10'] / divisor), 2)
        rating_dict['count'] = divisor

    else:
        # It is for that subjects whose feedback has not been submitted yet.
        rating_dict['count'] = divisor

    print(rating_dict)
    return rating_dict


def ratings_detailed(feedback_qs):
    total_feedback_count = feedback_qs.count()
    rating = {
        "Q1": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q2": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q3": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q4": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q5": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q6": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q7": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q8": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q9": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        "Q10": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
    }

    # ================= for rating["Q1"] =========================================
    Q1_one_rating_qs = feedback_qs.filter(Q1=1)
    rating["Q1"][1] = round(((Q1_one_rating_qs.count()/total_feedback_count) * 100), 2)
    Q1_two_rating_qs = feedback_qs.filter(Q1=2)
    rating["Q1"][2] = round(((Q1_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q1_three_rating_qs = feedback_qs.filter(Q1=3)
    rating["Q1"][3] = round(((Q1_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q1_four_rating_qs = feedback_qs.filter(Q1=4)
    rating["Q1"][4] = round(((Q1_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q1"][5] = 100 - (rating["Q1"][1] + rating["Q1"][2] + rating["Q1"][3] + rating["Q1"][4])
    # ================= for rating["Q2"] =========================================
    Q2_one_rating_qs = feedback_qs.filter(Q2=1)
    rating["Q2"][1] = round(((Q2_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q2_two_rating_qs = feedback_qs.filter(Q2=2)
    rating["Q2"][2] = round(((Q2_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q2_three_rating_qs = feedback_qs.filter(Q2=3)
    rating["Q2"][3] = round(((Q2_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q2_four_rating_qs = feedback_qs.filter(Q2=4)
    rating["Q2"][4] = round(((Q2_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q2"][5] = 100 - (rating["Q2"][1] + rating["Q2"][2] + rating["Q2"][3] + rating["Q2"][4])
    # ================= for rating["Q3"] =========================================
    Q3_one_rating_qs = feedback_qs.filter(Q3=1)
    rating["Q3"][1] = round(((Q3_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q3_two_rating_qs = feedback_qs.filter(Q3=2)
    rating["Q3"][2] = round(((Q3_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q3_three_rating_qs = feedback_qs.filter(Q3=3)
    rating["Q3"][3] = round(((Q3_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q3_four_rating_qs = feedback_qs.filter(Q3=4)
    rating["Q3"][4] = round(((Q3_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q3"][5] = 100 - (rating["Q3"][1] + rating["Q3"][2] + rating["Q3"][3] + rating["Q3"][4])
    # ================= for rating["Q4"] =========================================
    Q4_one_rating_qs = feedback_qs.filter(Q4=1)
    rating["Q4"][1] = round(((Q4_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q4_two_rating_qs = feedback_qs.filter(Q4=2)
    rating["Q4"][2] = round(((Q4_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q4_three_rating_qs = feedback_qs.filter(Q4=3)
    rating["Q4"][3] = round(((Q4_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q4_four_rating_qs = feedback_qs.filter(Q4=4)
    rating["Q4"][4] = round(((Q4_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q4"][5] = 100 - (rating["Q4"][1] + rating["Q4"][2] + rating["Q4"][3] + rating["Q4"][4])
    # ================= for rating["Q5"] =========================================
    Q5_one_rating_qs = feedback_qs.filter(Q5=1)
    rating["Q5"][1] = round(((Q5_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q5_two_rating_qs = feedback_qs.filter(Q5=2)
    rating["Q5"][2] = round(((Q5_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q5_three_rating_qs = feedback_qs.filter(Q5=3)
    rating["Q5"][3] = round(((Q5_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q5_four_rating_qs = feedback_qs.filter(Q5=4)
    rating["Q5"][4] = round(((Q5_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q5"][5] = 100 - (rating["Q5"][1] + rating["Q5"][2] + rating["Q5"][3] + rating["Q5"][4])
    # ================= for rating["Q6"] =========================================
    Q6_one_rating_qs = feedback_qs.filter(Q6=1)
    rating["Q6"][1] = round(((Q6_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q6_two_rating_qs = feedback_qs.filter(Q6=2)
    rating["Q6"][2] = round(((Q6_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q6_three_rating_qs = feedback_qs.filter(Q6=3)
    rating["Q6"][3] = round(((Q6_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q6_four_rating_qs = feedback_qs.filter(Q6=4)
    rating["Q6"][4] = round(((Q6_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q6"][5] = 100 - (rating["Q6"][1] + rating["Q6"][2] + rating["Q6"][3] + rating["Q6"][4])
    # ================= for rating["Q7"] =========================================
    Q7_one_rating_qs = feedback_qs.filter(Q7=1)
    rating["Q7"][1] = round(((Q7_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q7_two_rating_qs = feedback_qs.filter(Q7=2)
    rating["Q7"][2] = round(((Q7_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q7_three_rating_qs = feedback_qs.filter(Q7=3)
    rating["Q7"][3] = round(((Q7_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q7_four_rating_qs = feedback_qs.filter(Q7=4)
    rating["Q7"][4] = round(((Q7_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q7"][5] = 100 - (rating["Q7"][1] + rating["Q7"][2] + rating["Q7"][3] + rating["Q7"][4])
    # ================= for rating["Q8"] =========================================
    Q8_one_rating_qs = feedback_qs.filter(Q8=1)
    rating["Q8"][1] = round(((Q8_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q8_two_rating_qs = feedback_qs.filter(Q8=2)
    rating["Q8"][2] = round(((Q8_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q8_three_rating_qs = feedback_qs.filter(Q8=3)
    rating["Q8"][3] = round(((Q8_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q8_four_rating_qs = feedback_qs.filter(Q8=4)
    rating["Q8"][4] = round(((Q8_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q8"][5] = 100 - (rating["Q8"][1] + rating["Q8"][2] + rating["Q8"][3] + rating["Q8"][4])
    # ================= for rating["Q9"] =========================================
    Q9_one_rating_qs = feedback_qs.filter(Q9=1)
    rating["Q9"][1] = round(((Q9_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q9_two_rating_qs = feedback_qs.filter(Q9=2)
    rating["Q9"][2] = round(((Q9_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q9_three_rating_qs = feedback_qs.filter(Q9=3)
    rating["Q9"][3] = round(((Q9_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q9_four_rating_qs = feedback_qs.filter(Q9=4)
    rating["Q9"][4] = round(((Q9_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q9"][5] = 100 - (rating["Q9"][1] + rating["Q9"][2] + rating["Q9"][3] + rating["Q9"][4])
    # ================= for rating["Q10"] ========================================
    Q10_one_rating_qs = feedback_qs.filter(Q10=1)
    rating["Q10"][1] = round(((Q10_one_rating_qs.count() / total_feedback_count) * 100), 2)
    Q10_two_rating_qs = feedback_qs.filter(Q10=2)
    rating["Q10"][2] = round(((Q10_two_rating_qs.count() / total_feedback_count) * 100), 2)
    Q10_three_rating_qs = feedback_qs.filter(Q10=3)
    rating["Q10"][3] = round(((Q10_three_rating_qs.count() / total_feedback_count) * 100), 2)
    Q10_four_rating_qs = feedback_qs.filter(Q10=4)
    rating["Q10"][4] = round(((Q10_four_rating_qs.count() / total_feedback_count) * 100), 2)

    rating["Q10"][5] = 100 - (rating["Q10"][1] + rating["Q10"][2] + rating["Q10"][3] + rating["Q10"][4])

    print(rating)
    return rating


def serialize_detailed_feedback(feedback_qs):
    feedback_dict = []
    for i in feedback_qs:
        tmp = {
            'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p")),
            'q1': i.Q1, 'q2': i.Q2, 'q3': i.Q3, 'q4': i.Q4, 'q5': i.Q5,
            'q6': i.Q6, 'q7': i.Q7, 'q8': i.Q8, 'q9': i.Q9, 'q10': i.Q10,
            'remark': i.remarks
        }
        feedback_dict.append(tmp)

    print(feedback_dict)
    return feedback_dict