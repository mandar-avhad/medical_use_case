import streamlit as st
import pandas as pd
import json
import os
from model_predictions import get_predictions

# Load symptoms and medical history data from CSV files
symptoms_data = pd.read_csv('symptoms.csv')
symp_quest = pd.read_csv("questions.csv")
# question keyword mapping
# df_quest_map = pd.read_csv("all_disease_unique_symptoms (1).csv")
df_quest_map = pd.read_csv("mapping_file_new 1.csv")

history_data = pd.read_csv('other_questions.csv')
medical_history_data = history_data[history_data['Category'] == "medical history"]
personal_info = history_data[history_data['Category'] == "personal info"]
fam_medical_history_data = history_data[history_data['Category'] == "family medical history"]

# read json file to extract answers list to questions
f = open('release_evidences.json')
data = json.load(f)

quest_ans_dict = {}
for item in data.values():
    if item["value_meaning"]:
        question_en = item["question_en"]
        value_meaning = [value["en"] for value in item["value_meaning"].values()]
        quest_ans_dict[question_en] = value_meaning
    elif not item["value_meaning"] and item['possible-values']:
        question_en = item["question_en"]
        possible_values = item["possible-values"]
        quest_ans_dict[question_en] = possible_values

# filtering the symptom question answers from this dict
# filtered_symp_quest_dict = {key: value for key, value in quest_ans_dict.items() if key in symp_quest['Symptom_Questions'].values}
filtered_symp_quest_dict = {df_quest_map[df_quest_map['EVIDENCE'] == key]['KEYWORD_PA'].iloc[0]: value for key, value in quest_ans_dict.items() if key in symp_quest['Symptom_Questions'].values}

##########
# Create a list of questions to be removed
# questions_to_remove = [key for key in filtered_symp_quest_dict.keys() if key in symp_quest['Symptom_Questions'].values]
questions_to_remove = [key for key in filtered_symp_quest_dict.keys() if df_quest_map[df_quest_map['KEYWORD_PA'] == key]['EVIDENCE'].iloc[0] in symp_quest['Symptom_Questions'].values]

merged_symp_df = pd.merge(symp_quest, df_quest_map, left_on='Symptom_Questions', right_on='EVIDENCE', how='left')

# Remove the rows with questions in the list
symp_quest = merged_symp_df[~merged_symp_df['KEYWORD_PA'].isin(questions_to_remove)]

#########


# filtering the personal info question answers from this dict
# filtered_per_quest_dict = {key: value for key, value in quest_ans_dict.items() if key in personal_info['Questions'].values}
filtered_per_quest_dict = {df_quest_map[df_quest_map['EVIDENCE'] == key]['KEYWORD_PA'].iloc[0]: value for key, value in quest_ans_dict.items() if key in personal_info['Questions'].values}

# Create a list of questions to be removed
questions_to_remove = [key for key in filtered_per_quest_dict.keys() if df_quest_map[df_quest_map['KEYWORD_PA'] == key]['EVIDENCE'].iloc[0] in personal_info['Questions'].values]

merged_per_df = pd.merge(personal_info, df_quest_map, left_on='Questions', right_on='EVIDENCE', how='left')

# Remove the rows with questions in the list
per_quest = merged_per_df[~merged_per_df['KEYWORD_PA'].isin(questions_to_remove)]
#########

# final_responses = {}
# Initialize a global variable to store the disease predictions
if "st.session_state.final_responses" not in st.session_state:
    st.session_state.final_responses = {}

# Create a Streamlit app
st.title("Diagnoseme")

# Create Streamlit app
st.header("Patient Information")

# Create a text input for the user's name
name = st.text_input("Name")

# Create a number input for the user's age
age = st.number_input("Age", min_value=0)

# Create radio buttons for gender
gender = st.radio("Sex", ["Male", "Female"])

# storing
st.session_state.final_responses['NAME'] = name
st.session_state.final_responses['AGE'] = age
st.session_state.final_responses['SEX'] = gender

######################

# Question 1: Select the symptoms
st.header("Symptoms")
selected_symptoms = st.multiselect("Select the applicable symptoms:", symptoms_data['Symptoms'])

# adding this to handle new cases apart from our data
other_symp = st.text_input("Specify other symptoms if any:")
if other_symp != "":
    selected_symptoms.append(other_symp)
# storing
st.session_state.final_responses['symptoms'] = selected_symptoms

# Question 2: Select the questions related to symptoms
st.header("Questions related to symptoms")
# merged_df = pd.merge(symp_quest, df_quest_map, left_on='Symptom_Questions', right_on='EVIDENCE', how='left')
selected_symptoms_quest = st.multiselect("Select all the applicable symptom questions:", symp_quest['KEYWORD_PA'])

# adding this to handle new cases apart from our data
other_symp_quest = st.text_input("Specify other symptoms questions if any:")
if other_symp_quest != "":
    selected_symptoms_quest.append(other_symp_quest)

# selected_symptoms_quest = st.multiselect("Select all the applicable symptom questions:", symp_quest['Symptom_Questions'])

# mapping the required keyword
if len(selected_symptoms_quest) == 0:
    # handling exceptions if no questions answered
    selected_symptoms_quest_new = ""
else:
    # selected_symptoms_quest_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_symptoms_quest[0]]['KEYWORD_PA'].iloc[0]
    # filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_symptoms_quest)]
    # keywords_list = filtered_df['KEYWORD_PA'].tolist()
    # selected_symptoms_quest_new = ', '.join(keywords_list)
    selected_symptoms_quest_new = ', '.join(selected_symptoms_quest)

# storing
st.session_state.final_responses['symptoms_quest'] = selected_symptoms_quest_new

# Initialize a session state to keep track of the current question and responses
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = "Question 1"

# Allow the user to select a question
# selected_question = st.selectbox("Select and answer the applicable symptom questions from the dropdown one by one:", list(filtered_symp_quest_dict.keys()))

####
# temp, keyword mapping
# Create a dictionary mapping questions to keywords
# question_keyword_mapping = dict(zip(df_quest_map["EVIDENCE"], df_quest_map["KEYWORD_PA"]))

# # Your list of questions
# questions = list(filtered_symp_quest_dict.keys())

# # Create a new list with keywords
# keyword_list = [question_keyword_mapping.get(q, []) for q in questions]
df_filter_symp = pd.DataFrame(filtered_symp_quest_dict.items(), columns=['Questions', 'Answers'])

selected_question = st.selectbox("Select and answer the applicable symptom questions from the dropdown one by one:", df_filter_symp['Questions'])

#########

if selected_question != st.session_state.current_question:
    st.session_state.current_question = selected_question

# Create a dropdown for selecting an answer based on the selected question
selected_answer = st.selectbox("Select an answer:", filtered_symp_quest_dict[st.session_state.current_question])

# Store the user's response for the current question
if st.button("Submit Symptoms Response"):
    current_responses = st.session_state.responses.get(st.session_state.current_question, [])
    if selected_answer not in current_responses:
        current_responses.append(selected_answer)
        st.session_state.responses[st.session_state.current_question] = current_responses

st.session_state.final_responses['symptoms_quest_dropdown'] = []
# Display the user's responses for each question
st.write("Responses:")
for question, answers in st.session_state.responses.items():
    # st.write(f"{question}: {', '.join(answers)}")
    st.write(f"{question}: {', '.join(map(str, answers))}")

    # mapping the required keyword
    # question_new = df_quest_map[df_quest_map['EVIDENCE'] == question]['KEYWORD_PA'].iloc[0]

    # Access the list within the 'symptoms_quest_dropdown' dictionary
    existing_list = st.session_state.final_responses['symptoms_quest_dropdown']
    # # Add the new dictionary to the list
    existing_list.append({question:answers})
    
    # storing
    # st.session_state.final_responses['symptoms_quest_dropdown'] = {question:answers} 
    st.session_state.final_responses['symptoms_quest_dropdown'] = existing_list

# handling exceptions if no questions answered
if len(st.session_state.final_responses['symptoms_quest_dropdown']) == 0:
    st.session_state.final_responses['symptoms_quest_dropdown'] = ""

#########################################

# Question 2: Select medical history
st.header("Medical history")
medical_history_data_keyword = pd.merge(medical_history_data, df_quest_map, left_on='Questions', right_on='EVIDENCE', how='left')

selected_medical_history = st.multiselect("Select and answer the medical history questions applicable to you:", medical_history_data_keyword['KEYWORD_PA'])

# adding this to handle new cases apart from our data
other_med_hist = st.text_input("Specify other Medical History if any:")
if other_med_hist != "":
    selected_medical_history.append(other_med_hist)

# mapping the required keyword
if len(selected_medical_history) == 0:
    # handling exceptions if no questions answered
    selected_medical_history_new = ""
else:
    # selected_medical_history_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_medical_history[0]]['KEYWORD_PA'].iloc[0]
    # filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_medical_history)]
    # keywords_list = filtered_df['KEYWORD_PA'].tolist()
    # selected_medical_history_new = ', '.join(keywords_list)
    selected_medical_history_new = ', '.join(selected_medical_history)

st.session_state.final_responses['medical'] = selected_medical_history_new

# Question 3: Select family medical history
st.header("Family medical history")
fam_medical_history_keyword = pd.merge(fam_medical_history_data, df_quest_map, left_on='Questions', right_on='EVIDENCE', how='left')
selected_fam_medical_history = st.multiselect("Select and answer the family medical history questions applicable:", fam_medical_history_keyword['KEYWORD_PA'])

# adding this to handle new cases apart from our data
other_fam_med_hist = st.text_input("Specify other Family Medical History if any:")
if other_fam_med_hist != "":
    selected_fam_medical_history.append(other_fam_med_hist)

# mapping the required keyword
if len(selected_fam_medical_history) == 0:
    # handling exceptions if no questions answered
    selected_fam_medical_history_new = ""
else:
    # selected_fam_medical_history_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_fam_medical_history[0]]['KEYWORD_PA'].iloc[0]
    # filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_fam_medical_history)]
    # keywords_list = filtered_df['KEYWORD_PA'].tolist()
    # selected_fam_medical_history_new = ', '.join(keywords_list)
    selected_fam_medical_history_new = ', '.join(selected_fam_medical_history)

st.session_state.final_responses['fam_medical'] = selected_fam_medical_history_new

# Question 4: Select personal info
st.header("Personal information")
# per_quest_keyword = pd.merge(per_quest, df_quest_map, left_on='Questions', right_on='EVIDENCE', how='left')
selected_personal_info = st.multiselect("Select and answer the personal information questions applicable to you:", per_quest['KEYWORD_PA'])

# adding this to handle new cases apart from our data
other_per_hist = st.text_input("Specify other Personal History if any:")
if other_per_hist != "":
    selected_personal_info.append(other_per_hist)

# mapping the required keyword
if len(selected_personal_info) == 0:
    # handling exceptions if no questions answered
    selected_personal_info_new = "" # []
else:
    # selected_personal_info_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_personal_info[0]]['KEYWORD_PA'] # .iloc[0]
    # filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_personal_info)]
    # keywords_list = filtered_df['KEYWORD_PA'].tolist()
    # selected_personal_info_new = ', '.join(keywords_list)
    selected_personal_info_new = ', '.join(selected_personal_info)

st.session_state.final_responses['personal'] = selected_personal_info_new

#####################################
# only 1 quest in personal info with dropdown answers
# simple dropdown
selected_question = st.selectbox("Select the applicable personal questions and answer from the dropdown one by one:", list(filtered_per_quest_dict.keys()))

# Create a dropdown for selecting an answer based on the selected question
selected_answer = st.selectbox("Select answer:", filtered_per_quest_dict[selected_question])

# Button to submit the response
if st.button("Submit Personal Response"):
    if selected_question != "Select a Question" and selected_answer:
        # Store the response or perform any necessary action
        st.write(f"Question: {selected_question}")
        st.write(f"Answer: {selected_answer}")
        
        # # mapping the required keyword
        # selected_personal_info_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_personal_info]['KEYWORD_PA'].iloc[0]
        # mapping the required keyword
        # selected_question = df_quest_map[df_quest_map['EVIDENCE'] == selected_question]['KEYWORD_PA'].iloc[0]

        # You can add code to store responses in a database, file, or any other desired location
        st.session_state.final_responses['personal1'] = {selected_question:selected_answer}

# getting response in required format for model inference
data = st.session_state.final_responses
# st.write(f"og_dict:{data}")

# doing this for getting the string for model 2
if 'personal1' not in data:
    data['personal1'] = ""
elif 'medical' not in data:
    data['medical'] = ""
elif 'personal' not in data:   
    data['personal'] = ""
elif 'fam_medical' not in data:
    data['fam_medical'] = ""
elif 'symptoms_quest' not in data:
    data['symptoms_quest'] = ""
elif 'symptoms_quest_dropdown' not in data:
    data['symptoms_quest_dropdown'] = ""

# temp
symptom_dict = {}
symptom_dict['symptoms'] = data['symptoms']

symptoms = data['symptoms_quest']
dropdown_info = []

for item in data['symptoms_quest_dropdown']:
    key, value = list(item.items())[0]
    if isinstance(value, list):
        # to convert items from int to str in list
        value = [str(item) for item in value]
        value_str = ', '.join(value)
    else:
        value_str = str(value)
    dropdown_info.append(f"{key}:{{{value_str}}}")

formatted_string_2 = f"{symptoms} | {' | '.join(dropdown_info)}"

# doing this to separate the symptoms questions and add them with comma separated symptoms
# and keep only the dropdown symptoms in this

formatted_string_list = formatted_string_2.split(" | ")
symp_quest = formatted_string_list.pop(0)

formatted_string_2 = ' | '.join(formatted_string_list)

final_symptoms = symp_quest.split(', ')

# Append the new_symptoms
symptom_dict['symptoms'] += final_symptoms

formatted_string_1 = "AGE:{" + str(data['AGE']) + "} | SEX:{" + data['SEX'] + "} | Symptoms are:{" + ', '.join(symptom_dict['symptoms']) + "} | Medical History is:{" + data['medical'] + "} | Personal Information is:{" + data['personal'] + "} | Family Medical History is:{" + data['fam_medical'] + "} | "#  | Patient travelled to:{" + data['personal1']['travelled in last 4 weeks to'] + "}"


if 'personal1' in data and 'travelled in last 4 weeks to' in data['personal1']:
    formatted_string_3 = "| Patient travelled to:{" + data['personal1']['travelled in last 4 weeks to'] + "}"
else:
    formatted_string_3 = ""

# final string
model_2_string = formatted_string_1 + formatted_string_2 + formatted_string_3

# Initialize a global variable to store the disease predictions
if "final_str_2" not in st.session_state:
    st.session_state.final_str_2 = ""

st.session_state.final_str_2 = model_2_string

# temp
del data['personal1']
# model 2 string end


result = []

# Iterate through the dictionary and format the key-value pairs
for key, value in data.items():
    if isinstance(value, list):
        if key == 'symptoms':
            result.append(", ".join(value))
        elif key == 'symptoms_quest':
            result.append(value)
        else:
            for item in value:
                for sub_key, sub_value in item.items():
                    result.append(f"{sub_key} {', '.join(map(str, sub_value))}")
    elif isinstance(value, dict):
        for sub_key, sub_value in value.items():
            result.append(f"{sub_key} {sub_value}")
    else:
        result.append(f"{key} is {str(value)}")

# Initialize a global variable to store the disease predictions
if "final_str" not in st.session_state:
    st.session_state.final_str = ""

try:
    # Join the formatted key-value pairs with newlines
    formatted_string = "\n".join(result)
    formatted_string = formatted_string.replace("symptoms_quest_dropdown is ", "").replace("symptoms_quest is ", "").replace("personal is ", "").replace("medical is ", "").replace("fam_", "")
    new_str = ", ".join(formatted_string.split("\n"))
    
    st.session_state.final_str = " ".join(new_str.split())

    parts = st.session_state.final_str.split(', ')

    # Filter out empty elements (consecutive commas) and join with a single comma
    output_string = ', '.join(filter(None, parts))
    st.session_state.final_str = output_string.replace(", ,", "")

except Exception as e:
    print(e, "----")
    print("all questions are not yet answered")
    st.session_state.final_str = ""

st.write(f"Model_1_input: {st.session_state.final_str}")
st.write(f"Model_2_input: {st.session_state.final_str_2}")

# Predictions
st.header("Disease Predictions")

# Initialize a global variable to store the disease predictions
if "disease_data_M1" not in st.session_state:
    st.session_state.disease_data_M1 = []
if "disease_data_M2" not in st.session_state:
    st.session_state.disease_data_M2 = []

# Add a dropdown to select a model
# selected_model = st.selectbox("Select a Model", ['bert', 'all_mini'])
# st.write("Two Models Selected: bert, all_mini")

if st.button("Get Predictions"):
    if len(st.session_state.final_str) != 0:
        # disease_pred = get_predictions(st.session_state.final_str)
        # by default, do predictions for both the models, don't give options

        # M1 pred
        selected_model = "bert"
        disease_pred_M1 = get_predictions(st.session_state.final_str, selected_model)

        final_disease_pred_M1 = [f'{item[0]}: {item[1]*100:.5f}' for item in disease_pred_M1]

        # st.subheader(f"Top 3 disease predictions by Model 1: bert:")
        # for item in final_disease_pred_M1:
        #     st.write(item)

        # Store the predictions in the session state variable
        st.session_state.disease_data_M1 = final_disease_pred_M1

        #########
        # M2 pred
        selected_model = "all_mini"
        disease_pred_M2 = get_predictions(st.session_state.final_str_2, selected_model)

        final_disease_pred_M2 = [f'{item[0]}: {item[1]*100:.5f}' for item in disease_pred_M2]

        # st.subheader(f"Top 3 disease predictions by Model 2: all_mini:")
        # for item in final_disease_pred_M2:
        #     st.write(item)

        # Store the predictions in the session state variable
        st.session_state.disease_data_M2 = final_disease_pred_M2

    else:
        st.write("First fill the entire form and then get predictions")


if len(st.session_state.disease_data_M1) > 0:
    st.subheader(f"Top 3 disease predictions by both the models:")
    # creating df to display
    data = {
        'Model_1_ClinicalBERT': [st.session_state.disease_data_M1[0], st.session_state.disease_data_M1[1], st.session_state.disease_data_M1[2]],
        'Model_2_AllMini': [st.session_state.disease_data_M2[0], st.session_state.disease_data_M2[1], st.session_state.disease_data_M2[2]]
    }
    index_names = ['Label 1', 'Label 2', 'Label 3']
    df = pd.DataFrame(data, index=index_names)
    # table
    st.table(df)

if len(st.session_state.disease_data_M1) > 0:
    is_correct_M1 = st.radio("Model 1 Predictions are:", ("Correct", "Incorrect"))
    is_correct_M2 = st.radio("Model 2 Predictions are:", ("Correct", "Incorrect"))
    feedback = st.text_input("Provide feedback (optional) if incorrect predictions")
    
    st.session_state.final_responses["is_correct_M1"] = is_correct_M1
    st.session_state.final_responses["is_correct_M2"] = is_correct_M2
    st.session_state.final_responses["feedback"] = feedback

# Initialize a global variable to store the disease predictions
if "data_to_write" not in st.session_state:
    st.session_state.data_to_write = {}

if len(st.session_state.disease_data_M1) > 0:
    if st.button("Write data to CSV"):
        # store data for writing to csv after pred
        patient_id = st.session_state.final_responses['NAME'] + "_" + str(st.session_state.final_responses['AGE'])
        patient_string_M1 = st.session_state.final_str
        patient_string_M2 = st.session_state.final_str_2

        # get label names and percent for M1
        label_names_M1 = [item.split(': ')[0] for item in st.session_state.disease_data_M1]
        percent_list_M1 = [item.split(': ')[1] for item in st.session_state.disease_data_M1]
        
        label_1_M1 = label_names_M1[0]
        label_1_percent_M1 = percent_list_M1[0]

        label_2_M1 = label_names_M1[1]
        label_2_percent_M1 = percent_list_M1[1]

        label_3_M1 = label_names_M1[2]
        label_3_percent_M1 = percent_list_M1[2]
        
        # get label names and percent for M1
        label_names_M2 = [item.split(': ')[0] for item in st.session_state.disease_data_M2]
        percent_list_M2 = [item.split(': ')[1] for item in st.session_state.disease_data_M2]
        
        label_1_M2 = label_names_M2[0]
        label_1_percent_M2 = percent_list_M2[0]

        label_2_M2 = label_names_M2[1]
        label_2_percent_M2 = percent_list_M2[1]

        label_3_M2 = label_names_M2[2]
        label_3_percent_M2 = percent_list_M2[2]

        st.session_state.data_to_write = {}
        st.session_state.data_to_write = {
        "Patient_ID": [patient_id],
        "Patient_String_M1": [patient_string_M1],
        "Label_1_M1": [label_1_M1],
        "Label_1%_M1": [label_1_percent_M1],
        "Label_2_M1": [label_2_M1],
        "Label_2%_M1": [label_2_percent_M1],
        "Label_3_M1": [label_3_M1],
        "Label_3%_M1": [label_3_percent_M1],
        
        "Patient_String_M2": [patient_string_M2],
        "Label_1_M2": [label_1_M2],
        "Label_1%_M2": [label_1_percent_M2],
        "Label_2_M2": [label_2_M2],
        "Label_2%_M2": [label_2_percent_M2],
        "Label_3_M2": [label_3_M2],
        "Label_3%_M2": [label_3_percent_M2]
        }

        # comment below condition
        # if st.session_state.final_responses["is_correct"] == "Correct":
        #     st.session_state.data_to_write['Correct'] = ["Yes"]
        #     st.session_state.data_to_write['Incorrect'] = ["No"]
        # else:
        #     st.session_state.data_to_write['Correct'] = ["No"]
        #     st.session_state.data_to_write['Incorrect'] = ["Yes"]
        
        st.session_state.data_to_write["Results_M1"] = [st.session_state.final_responses["is_correct_M1"]]
        st.session_state.data_to_write["Results_M2"] = [st.session_state.final_responses["is_correct_M2"]]

        st.session_state.data_to_write["Feedback"] = [st.session_state.final_responses["feedback"]]
        
        df = pd.DataFrame(st.session_state.data_to_write)
        
        st.write(df)
        file_path = 'verify_predictions.csv'
        if not os.path.exists(file_path):
            df.to_csv(file_path, index=False)
        else:
            df.to_csv(file_path, index=False, mode='a', header=False)

        st.success("Data saved to CSV file 'verify_predictions.csv'")
        
        ##################
        # saving data to db
        import pyodbc
        import pandas as pd
        from urllib import parse
        from sqlalchemy import create_engine
        from sqlalchemy import text

        # db read, write functions
        def database_write(dataframe, table_name):
            sql_conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:sqldiagnoseme.database.windows.net,1433;Database=sql-db-diagnoseme;Uid=sqladmin;Pwd=Themathcompany@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            params = parse.quote_plus(sql_conn_str)
            engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" %params, future=True)
            dataframe.to_sql(table_name, engine, if_exists='append', index=False)
            print("Data writing to database is completed!!!")

        database_write(df, "results_streamlit")
        st.success("Data writing to database is completed!!!")
        ##################

        # Downloading the csv data
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        df_updated = pd.read_csv("verify_predictions.csv")
        csv = convert_df(df_updated)

        st.download_button(
            "Download CSV",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
            )

