import pandas as pd
import random as r
import math
import os
from datetime import datetime

def gen_data(dirPath, course_num, num_teacher, min_class, max_class, recruit_student, student_min_in_class, student_in_class, max_reg_a_class):
    file_suffix = str(course_num) + '-' + str(num_teacher) #+ '-' + datetime.now().strftime('%H%M%S')

    max_class = max_class if (min_class < max_class) else min_class + 1

    gen_teachers = [ {'TeacherID': 'T' + str(x+1).zfill(2), 'TeacherName':'Teacher '+ "{:02d}".format(x+1),'Max Classes':r.randrange(min_class, max_class)} for x in range(num_teacher)]
    gen_teachers = pd.DataFrame(gen_teachers)
    gen_teachers.to_csv(dirPath + '/Teachers-' + file_suffix + '.csv')

    print('########################## TEACHERS ##########################')
    print(gen_teachers)
    print('##############################################################')
    # gen number of students 
    alloc_student = 0
    gen_students = []
    for x in range(course_num):
        students_in_course = {}
        students_in_course['CourseID'] = 'C' + str(x).zfill(2)

        #r0 = max_reg_a_class if (max_reg_a_class == student_in_class and student_in_class == student_min_in_class) else 0
        r0 = 0

        student_reg = max_reg_a_class if (max_reg_a_class == student_in_class and student_in_class == student_min_in_class) else r.randrange(r0, max_reg_a_class)
        student_reg = student_reg if (recruit_student - alloc_student) > student_reg else recruit_student - alloc_student
        students_in_course['No Students'] = student_reg if student_reg > 0 else 0
        alloc_student += student_reg
        gen_students.append(students_in_course)

    gen_students = pd.DataFrame(gen_students)
    print('########################## STUDENTS ##########################')
    print(gen_students)
    print('##############################################################')

    gen_classes = [ {'CourseID': 'C' + str(x+1).zfill(2), 
                    'Course Name':'Course '+ "{:02d}".format(x+1),
                    'Basic': r.randrange(1, 4) % 2, 
                    'No. Classes': None if math.floor(gen_students.at[x, 'No Students'] / student_min_in_class) == 0 else math.ceil(gen_students.at[x, 'No Students'] / student_in_class)} for x in range(course_num)]

    gen_classes = pd.DataFrame(gen_classes)
    gen_classes.to_csv(dirPath +'/Courses-' + file_suffix + '.csv')

    print('########################### COURSES ##########################')
    print(gen_classes)
    print('##############################################################')

    teacher_class = {}    
    for y in range(num_teacher):
        t = gen_teachers.at[y, 'Max Classes'] if (max_class != min_class + 1) else course_num
        max_pref = r.randrange(t, gen_teachers.at[y, 'Max Classes'] + 8) if (t < course_num) else course_num
        teacher_class['T' + str(y + 1).zfill(2)] = list(range(1, max_pref + 1))

    full_registration = []
    assign_course_num = course_num
    

    for x in range(course_num):
        registration = { 'Course\Teacher' : 'C' + str(x+1).zfill(2) }
        assign_num_teacher = num_teacher
        
        for y in range(assign_num_teacher):
            teacher_key = 'T' + str(y+1).zfill(2)
            assign_class = teacher_class.get(teacher_key)
            list_len = len(assign_class)

            if assign_course_num > list_len and r.randrange(1,4) % 2 == 0:
                if list_len > 0:
                    index = r.randint(0, list_len)
                    assigned = int(assign_class.pop(index)) if list_len != index else int(assign_class.pop(0))
                else: 
                    assigned = None
                registration[teacher_key] = assigned
            elif assign_course_num <= list_len:
                index = r.randint(0, assign_course_num)                
                assigned = int(assign_class.pop(index)) if list_len != index else int(assign_class.pop(0)) # if list_len < 3 else int(assign_class.pop(r.randint(0, list_len)))
                registration[teacher_key] = assigned
            else:             
                registration[teacher_key] = None
            teacher_class[teacher_key] = assign_class
                    
        assign_course_num -= 1    
        full_registration.append(registration)

    full_registration = pd.DataFrame(full_registration)
    full_registration.to_csv(dirPath + '/Registrations-' + file_suffix + '.csv')

    print('######################### REGISTRATIONS ########################')
    print(full_registration)
    print('################################################################')


course_num = int(input('Enter total course school offer: '))
num_teacher = int(input('Enter total of teachers school has: '))
min_class = int(input('Enter minimum classes a teacher must teach in a week: '))
max_class = int(input('Enter max classes a teacher must teach in a week: '))
#recruit_student = int(input('Enter number registered students: '))
#student_min_in_class = int(input('Enter number of minimum students for a class: '))
#student_in_class = int(input('Enter number of maximum students for a class: '))
#max_reg_a_class = int(input('Enter number of student in a class: '))

num_dataset = int(input('Number of DataSet: '))

directory = os.path.join('data')
try: 
    os.stat(directory)
except:
    os.mkdir(directory)  

for i in range(num_dataset) :
    dirPath = os.path.join(directory, 'dataset-' + str(i+1).zfill(2))
    try: 
        os.stat(dirPath)
    except:
        os.mkdir(dirPath)
        
    gen_data(dirPath, course_num, num_teacher, min_class, max_class, recruit_student=3000, student_min_in_class=15, student_in_class=30, max_reg_a_class=90)


