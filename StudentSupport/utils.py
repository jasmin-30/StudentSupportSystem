import datetime
import os

from django.http import HttpResponse

from StudentSupport.models import *
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import LabelOffset
from reportlab.graphics.shapes import Drawing, Image, String, Line
from reportlab.lib import colors
from reportlab.lib.formatters import DecimalFormatter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, TableStyle, Spacer, Table, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# Function for getting queryset of feedback
# input : faculty_obj : Faculty Object
# input : subject_obj : Subject Object
# fb_type : "mid" for mid semester feedback, "end" for end semester feedback
# year : year for which feedback is required.
def get_feedback_qs(faculty_obj, subject_obj, fb_type, year):
    fb_type = fb_type.lower()
    if fb_type == "mid":
        feedback_qs = Mid_Sem_Feedback_Answers.objects.filter(
            subject_id=subject_obj,
            faculty_id=faculty_obj,
            timestamp__year=year
        )
    elif fb_type == "end":
        feedback_qs = End_Sem_Feedback_Answers.objects.filter(
            subject_id=subject_obj,
            faculty_id=faculty_obj,
            timestamp__year=year
        )

    return feedback_qs


# Function for getting question wise average feedback for all subject of perticular faculty.
# def serialize_feedback(feedback_qs, faculty_obj, semester_list):
#     # feedback_distinct = feedback_qs.filter()
#     subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=faculty_obj,
#                                                            subject_id__semester__in=semester_list)
#     ratings = []
#     for i in subject_qs:
#         tmp = {
#             'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0, 'Q5': 0,
#             'Q6': 0, 'Q7': 0, 'Q8': 0, 'Q9': 0, 'Q10': 0,
#         }
#         print(i.subject_id.id, i.subject_id.subject_name)
#         tmp['subject_id'] = i.subject_id.id
#         tmp['subject_name'] = i.subject_id.subject_name
#         tmp['subject_code'] = i.subject_id.subject_code
#         tmp['subject_semester'] = i.subject_id.semester
#         feedback_distinct = feedback_qs.filter(subject_id_id=i.subject_id.id)
#         div = feedback_distinct.count()
#         if div > 0:
#             for j in feedback_distinct:
#                 # getting sum of all the feedback.
#                 tmp['Q1'] += j.Q1
#                 tmp['Q2'] += j.Q2
#                 tmp['Q3'] += j.Q3
#                 tmp['Q4'] += j.Q4
#                 tmp['Q5'] += j.Q5
#                 tmp['Q6'] += j.Q6
#                 tmp['Q7'] += j.Q7
#                 tmp['Q8'] += j.Q8
#                 tmp['Q9'] += j.Q9
#                 tmp['Q10'] += j.Q10
#
#             # calculating average of all the feedback
#             tmp['Q1'] = round((tmp['Q1'] / div), 2)
#             tmp['Q2'] = round((tmp['Q2'] / div), 2)
#             tmp['Q3'] = round((tmp['Q3'] / div), 2)
#             tmp['Q4'] = round((tmp['Q4'] / div), 2)
#             tmp['Q5'] = round((tmp['Q5'] / div), 2)
#             tmp['Q6'] = round((tmp['Q6'] / div), 2)
#             tmp['Q7'] = round((tmp['Q7'] / div), 2)
#             tmp['Q8'] = round((tmp['Q8'] / div), 2)
#             tmp['Q9'] = round((tmp['Q9'] / div), 2)
#             tmp['Q10'] = round((tmp['Q10'] / div), 2)
#             tmp['count'] = div
#
#         else:
#             # It is for that subjects whose feedback has not been submitted yet.
#             tmp['count'] = div
#             pass
#
#         # appending tmp dictionary into rating list
#         ratings.append(tmp)
#
#     # Returning ratings object
#     return ratings


# Function for getting question wise average feedback for all faculty of perticular subject.
def serialize_subjectwise_feedback(feedback_qs, subject_obj):
    faculty_qs = Subject_to_Faculty_Mapping.objects.filter(subject_id=subject_obj)
    ratings = []
    for i in faculty_qs:
        tmp = {
            'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0, 'Q5': 0,
            'Q6': 0, 'Q7': 0, 'Q8': 0, 'Q9': 0, 'Q10': 0,
        }
        print(i.subject_id.id, i.subject_id.subject_name)
        tmp['faculty_id'] = i.faculty_id.id
        tmp['faculty_name'] = i.faculty_id.name
        tmp['faculty_dept'] = i.faculty_id.dept_id.accronym
        feedback_distinct = feedback_qs.filter(faculty_id_id=i.faculty_id.id)
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
    rating["Q1"][1] = round(((Q1_one_rating_qs.count() / total_feedback_count) * 100), 2)
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
        if i.is_anonymous:
            tmp['anonymous'] = 1
            tmp['student_name'] = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp['student_enrollment'] = str(i.student_id.enrollment_no)
            tmp['student_dept'] = str(i.student_id.dept_id.dept_name) + " (Div - " + str(i.student_id.div) + ")"

        else:
            tmp['anonymous'] = 0
            tmp['student_name'] = "Anonymous"
            tmp['student_enrollment'] = "Anonymous"
            tmp['student_dept'] = "Anonymous"
        feedback_dict.append(tmp)

    print(feedback_dict)
    return feedback_dict


def make_avg_feedback_pdf(questionwise_ratings, rating_insights, subject_obj, fac_obj, question_qs, fb_type, term_type,
                          year):
    question_count = question_qs.count()
    pdfname1 = "Temp1"

    response1 = HttpResponse(content_type='application/pdf')
    response1['Content-Disposition'] = 'attachment; filename=' + pdfname1

    elements1 = []
    doc1 = SimpleDocTemplate(response1, rightMargin=inch / 4,
                             leftMargin=inch / 4,
                             topMargin=inch / 2,
                             bottomMargin=inch / 4,
                             pagesize=A4)

    path_to_file = os.getcwd() + "/logo.jpg"

    data_list = []
    label_list = []
    sum = 0
    for i in range(1, question_count + 1):
        index = "Q" + str(i)
        data_list.append(questionwise_ratings[index])
        sum += questionwise_ratings[index]
        label_list.append(("Question : " + str(i)))

    overall = round((sum/question_count), 2)

    text1 = "Government Engineering College, Bhavnagar"
    text2 = fb_type + " Semester Feedback Report"
    text3 = "Term: " + term_type + " " + str(year)
    text4 = "Date: " + str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
    text5 = str(subject_obj.dept_id.dept_name) + " Department" + " Div - " + str(subject_obj.div)
    text6 = str(fac_obj.name) + "( " + str(fac_obj.dept_id.accronym) + " Department )"
    text7 = "Subject Name: " + subject_obj.subject_name + " (" + subject_obj.subject_code + ")"
    text8 = "Semester: " + str(subject_obj.semester)
    text9 = "Total number of Feedback: " + str(questionwise_ratings["count"])
    text10 = "Overall Feedback: " + str(overall)

    d = Drawing(400, 200)
    d.add(Image(0, 120, 100, 100, path_to_file))
    d.add(String(120, 190, text1, fontSize=20, fillColor=colors.black))
    d.add(String(170, 150, text2, fontSize=18, fillColor=colors.black))
    d.add(String(30, 110, text3, fontSize=14, fillColor=colors.black))
    d.add(String(370, 110, text4, fontSize=14, fillColor=colors.black))
    d.add(Line(0, 90, 550, 90))
    d.add(String(130, 65, text5, fontSize=18, fillColor=colors.black))
    d.add(String(30, 35, text6, fontSize=12, fillColor=colors.black))
    d.add(String(30, 20, text7, fontSize=12, fillColor=colors.black))
    d.add(String(380, 20, text8, fontSize=12, fillColor=colors.black))
    d.add(String(22, -45, text10, fontSize=16, fillColor=colors.black))
    d.add(String(300, -45, text9, fontSize=12, fillColor=colors.black))

    elements1.append(d)

    drawing = Drawing(400, 200)
    drawing.vAlign = 'CENTER'

    data = []
    data.append(tuple(data_list))
    print(data)
    bc = VerticalBarChart()
    bc.x = 28
    bc.y = -120
    bc.height = 250
    bc.width = 500
    bc.data = data
    bc.bars[0].fillColor = colors.aqua
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 5.0
    bc.valueAxis.valueStep = 0.5
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = label_list
    bc.barLabels.angle = 0
    bc.barLabels.boxAnchor = 's'
    bc.barLabelFormat = DecimalFormatter(2)
    drawing.add(bc)

    elements1.append(drawing)

    elements1.append(PageBreak())

    ##################################################################################################################

    pdfname2 = "Temp1"
    response2 = HttpResponse(content_type='application/pdf')
    response2['Content-Disposition'] = 'attachment; filename=' + pdfname2

    elements2 = []
    doc2 = SimpleDocTemplate(response2, rightMargin=inch / 4,
                             leftMargin=inch / 4,
                             topMargin=inch / 2,
                             bottomMargin=inch / 4,
                             pagesize=A4)

    path_to_file = os.getcwd() + "/logo.jpg"

    text1 = "Government Engineering College, Bhavnagar"
    text2 = fb_type + " Semester Feedback Report"
    text3 = "Term: " + term_type + " " + str(year)
    text4 = "Date: " + str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
    text5 = "Total Feedback: " + str(questionwise_ratings["count"])

    d2 = Drawing(400, 200)
    d2.add(Image(0, 120, 100, 100, path_to_file))
    d2.add(String(120, 190, text1, fontSize=20, fillColor=colors.black))
    d2.add(String(170, 150, text2, fontSize=18, fillColor=colors.black))
    d2.add(String(30, 110, text3, fontSize=14, fillColor=colors.black))
    d2.add(String(370, 110, text4, fontSize=14, fillColor=colors.black))
    d2.add(Line(0, 90, 550, 90))
    d2.add(String(30, 70, text5, fontSize=12, fillColor=colors.black))

    elements2.append(d2)

    elements2.append(Spacer(550, -50))

    fl = [["Sr No", "Questions", "Feedback"]]
    for i in range(question_count):
        index = "Q" + str(i + 1)
        dpie = Drawing(200, 100)
        pc = Pie()
        pc.x = 65
        pc.y = 15
        pc.width = 70
        pc.height = 70
        pc.sideLabels = 1
        pc.data = [rating_insights[index][1], rating_insights[index][2], rating_insights[index][3],
                   rating_insights[index][4], rating_insights[index][5]]
        pc.labels = ['1', '2', '3', '4', '5']
        pc.slices.strokeWidth = 0.5
        pc.slices[0].fillColor = colors.red
        pc.slices[1].fillColor = colors.blue
        pc.slices[2].fillColor = colors.gray
        pc.slices[3].fillColor = colors.yellow
        pc.slices[4].fillColor = colors.green
        dpie.add(pc)
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 145
        legend.y = 90
        legend.columnMaximum = 5
        legend.dxTextSpace = 4
        n = len(pc.data)
        legend.colorNamePairs = [(pc.slices[i].fillColor, (pc.labels[i], ': ' + '%0.2f' % pc.data[i] + '%'))
                                 for i in
                                 range(n)]
        dpie.add(legend)

        style = getSampleStyleSheet()
        p = Paragraph(str(question_qs[i].question_text), style['Normal'])
        ft = [(i + 1), p, [dpie]]
        fl.append(ft)

    table = Table(fl)

    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                               ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ('BACKGROUND', (0, -1), (-1, -1), colors.white),
                               ]))
    table._argW[0] = 0.6 * inch
    table._argW[1] = 3.5 * inch
    table._argW[2] = 3.3 * inch

    table._argH[0] = 0.35 * inch
    for i in range(1, question_count + 1):
        table._argH[i] = 1.6 * inch

    table.spaceBefore = 0

    elements2.append(table)

    ##################################################################################################################

    pdfname3 = str(subject_obj.subject_name)
    pdfname3 = pdfname3.replace(" ", "_")
    response3 = HttpResponse(content_type='application/pdf')
    response3[
        'Content-Disposition'] = 'attachment; filename=' + pdfname3 + '_' + fb_type + '_Semester_Average_Feedback.pdf'
    elements3 = []

    doc3 = SimpleDocTemplate(response3, rightMargin=inch / 4,
                             leftMargin=inch / 4,
                             topMargin=inch / 2,
                             bottomMargin=inch / 4,
                             pagesize=A4)

    for i in elements1:
        elements3.append(i)

    for i in elements2:
        elements3.append(i)

    doc3.build(elements3)

    return response3


def make_detailed_feedback_pdf(serialized_feedback, subject_obj, fac_obj, fb_type, term_type, year, question_qs):
    question_count = question_qs.count()
    pdfname = str(subject_obj.subject_name)
    pdfname = pdfname.replace(" ", "_")
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'attachment; filename=' + pdfname + '_' + fb_type + '_Semester_Detailed_Feedback.pdf'

    elements = []

    doc = SimpleDocTemplate(response, rightMargin=inch / 4,
                            leftMargin=inch / 4,
                            topMargin=inch / 2,
                            bottomMargin=inch / 4,
                            pagesize=A4)

    path_to_file = os.getcwd() + "/logo.jpg"

    for k in serialized_feedback:

        text1 = "Government Engineering College, Bhavnagar"
        text2 = fb_type + " Semester Feedback Report"
        text3 = "Term: " + term_type + " " + str(year)
        text4 = "Date: " + str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
        text5 = str(subject_obj.dept_id.dept_name) + " Department" + " Div - " + str(subject_obj.div)
        text6 = str(fac_obj.name) + "( " + str(fac_obj.dept_id.accronym) + " Department )"
        text7 = "Subject Name: " + subject_obj.subject_name + " (" + subject_obj.subject_code + ")"
        text8 = "Semester: " + str(subject_obj.semester)
        text9 = "Date of Feedback: " + str(k['date'])
        text10 = "Student Name: " + str(k['student_name'])
        text11 = "Enrollment Number: " + str(k['student_enrollment'])
        text12 = "Department: " + str(k['student_dept'])

        d = Drawing(400, 200)
        d.add(Image(0, 120, 100, 100, path_to_file))
        d.add(String(120, 190, text1, fontSize=20, fillColor=colors.black))
        d.add(String(170, 150, text2, fontSize=18, fillColor=colors.black))
        d.add(String(30, 110, text3, fontSize=14, fillColor=colors.black))
        d.add(String(370, 110, text4, fontSize=14, fillColor=colors.black))
        d.add(Line(0, 90, 550, 90))
        d.add(String(130, 65, text5, fontSize=18, fillColor=colors.black))
        d.add(String(30, 35, text6, fontSize=12, fillColor=colors.black))
        d.add(String(30, 20, text7, fontSize=12, fillColor=colors.black))
        d.add(String(380, 20, text8, fontSize=12, fillColor=colors.black))
        if k['anonymous'] == 1:
            d.add(String(30, -10, text10, fontSize=12, fillColor=colors.black))
            d.add(String(300, -10, text11, fontSize=12, fillColor=colors.black))
            d.add(String(30, -25, text12, fontSize=12, fillColor=colors.black))
        d.add(String(300, -25, text9, fontSize=12, fillColor=colors.black))



        elements.append(d)
        elements.append(Spacer(500, 50))

        fl = [["Sr No", "Questions", "Feedback"]]
        for i in range(1, question_count + 1):
            index = "q" + str(i)
            styles = getSampleStyleSheet()
            p = Paragraph(str(question_qs[i - 1].question_text), styles['Normal'])
            ft = [i, p, k[index]]
            fl.append(ft)

        # fl.append([11, 'Remarks', l[k][10]])

        # data = fl
        # table = Table(data, 12 * [0.5 * inch])
        table = Table(fl)

        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                   ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                   ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                   ('BACKGROUND', (0, -1), (-1, -1), colors.white),
                                   ]))
        table._argW[0] = 1.0 * inch
        table._argW[1] = 4.0 * inch
        table._argW[2] = 2.0 * inch

        table._argH[0] = 0.5 * inch
        # for i in range(1, question_count + 1):
        #     table._argH[i] = 0.7 * inch

        # table._argH[1] = 0.4 * inch
        # table._argH[2] = 0.4 * inch
        # table._argH[3] = 0.4 * inch
        # table._argH[4] = 0.4 * inch
        # table._argH[5] = 0.4 * inch
        # table._argH[6] = 0.4 * inch
        # table._argH[7] = 0.4 * inch
        # table._argH[8] = 0.4 * inch
        # table._argH[9] = 0.4 * inch
        # table._argH[10] = 0.4 * inch
        # table._argH[11] = 0.4 * inch

        elements.append(table)

        drawing_for_remarks = Drawing(400, 200)
        drawing_for_remarks.add(
            String(22, 170, "Remarks: " + str(k['remark']), fontSize=12, fillColor=colors.black))

        drawing_for_remarks.add(
            String(22, 100, "Note: All the feedback given are out of 5.", fontSize=12,
                   fillColor=colors.black))

        elements.append(drawing_for_remarks)

        elements.append(PageBreak())

    doc.build(elements)
    return response
