import streamlit as st
import pandas as pd

# Load symptoms and medical history data from CSV files
symptoms_data = pd.read_csv('symptoms.csv')
symp_quest = pd.read_csv("questions.csv")
# question keyword mapping
df_quest_map = pd.read_csv("all_disease_unique_symptoms (1).csv")


history_data = pd.read_csv('other_questions.csv')
medical_history_data = history_data[history_data['Category'] == "medical history"]
personal_info = history_data[history_data['Category'] == "personal info"]
fam_medical_history_data = history_data[history_data['Category'] == "family medical history"]

import json
# read json file to extract answers list to questions
f = open('release_evidences.json')
data = json.load(f)

# converting the json into required quest:answer dict mapping
# quest_ans_dict = {
#     item["question_en"]: [value["en"] for value in item["value_meaning"].values()]
#     for item in data.values() if item["value_meaning"]
# }
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
filtered_symp_quest_dict = {key: value for key, value in quest_ans_dict.items() if key in symp_quest['Symptom_Questions'].values}
##########
# Create a list of questions to be removed
questions_to_remove = [key for key in filtered_symp_quest_dict.keys() if key in symp_quest['Symptom_Questions'].values]
# Remove the rows with questions in the list
symp_quest = symp_quest[~symp_quest['Symptom_Questions'].isin(questions_to_remove)]
#########


# filtering the personal info question answers from this dict
filtered_per_quest_dict = {key: value for key, value in quest_ans_dict.items() if key in personal_info['Questions'].values}
# Create a list of questions to be removed
questions_to_remove = [key for key in filtered_per_quest_dict.keys() if key in personal_info['Questions'].values]
# Remove the rows with questions in the list
per_quest = personal_info[~personal_info['Questions'].isin(questions_to_remove)]
#########

final_responses = {}

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
####
# storing
final_responses['NAME'] = name
final_responses['AGE'] = age
final_responses['SEX'] = gender

######################

# Question 1: Select the symptoms
st.header("Symptoms")
selected_symptoms = st.multiselect("Select the applicable symptoms:", symptoms_data['Symptoms'])
# storing
final_responses['symptoms'] = selected_symptoms
###

# Question 2: Select the questions related to symptoms
st.header("Questions related to symptoms")
selected_symptoms_quest = st.multiselect("Select all the applicable symptom questions:", symp_quest['Symptom_Questions'])

# mapping the required keyword
if len(selected_symptoms_quest) == 0:
    selected_symptoms_quest_new = []
else:
    # selected_symptoms_quest_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_symptoms_quest[0]]['KEYWORD'].iloc[0]
    filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_symptoms_quest)]
    keywords_list = filtered_df['KEYWORD'].tolist()
    selected_symptoms_quest_new = ', '.join(keywords_list)
    
# storing
final_responses['symptoms_quest'] = selected_symptoms_quest_new

####################################
# test dropdown
# symptom quest answers

# Initialize a session state to keep track of the current question and responses
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = "Question 1"

# st.header("Question and Answer Dropdowns")

# Allow the user to select a question
selected_question = st.selectbox("Select and answer the applicable symptom questions from the dropdown one by one:", list(filtered_symp_quest_dict.keys()))

if selected_question != st.session_state.current_question:
    st.session_state.current_question = selected_question

# Display the selected question
# st.write("You selected:", selected_question)

# Create a dropdown for selecting an answer based on the selected question
selected_answer = st.selectbox("Select an answer:", filtered_symp_quest_dict[st.session_state.current_question])

# Display the selected answer
# st.write("You selected:", selected_answer)

# Store the user's response for the current question
if st.button("Submit Response 1"):
    current_responses = st.session_state.responses.get(st.session_state.current_question, [])
    if selected_answer not in current_responses:
        current_responses.append(selected_answer)
        st.session_state.responses[st.session_state.current_question] = current_responses

# test
final_responses['symptoms_quest_dropdown'] = []
# Display the user's responses for each question
st.write("Responses:")
for question, answers in st.session_state.responses.items():
    # st.write(f"{question}: {', '.join(answers)}")
    st.write(f"{question}: {', '.join(map(str, answers))}")

    # mapping the required keyword
    question_new = df_quest_map[df_quest_map['EVIDENCE'] == question]['KEYWORD'].iloc[0]

    # Access the list within the 'symptoms_quest_dropdown' dictionary
    existing_list = final_responses['symptoms_quest_dropdown']
    # # Add the new dictionary to the list
    existing_list.append({question_new:answers})
    
    # storing
    # final_responses['symptoms_quest_dropdown'] = {question:answers} 
    final_responses['symptoms_quest_dropdown'] = existing_list

#########################################

# Question 2: Select medical history
st.header("Medical history")
selected_medical_history = st.multiselect("Select and answer the medical history questions applicable to you:", medical_history_data['Questions'])

# mapping the required keyword
if len(selected_medical_history) == 0:
    selected_medical_history_new = []
else:
    # selected_medical_history_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_medical_history[0]]['KEYWORD'].iloc[0]
    filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_medical_history)]
    keywords_list = filtered_df['KEYWORD'].tolist()
    selected_medical_history_new = ', '.join(keywords_list)

final_responses['medical'] = selected_medical_history_new
###

# Question 3: Select family medical history
st.header("Family medical history")
selected_fam_medical_history = st.multiselect("Select and answer the family medical history questions applicable:", fam_medical_history_data['Questions'])

# mapping the required keyword
if len(selected_fam_medical_history) == 0:
    selected_fam_medical_history_new = []
else:
    # selected_fam_medical_history_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_fam_medical_history[0]]['KEYWORD'].iloc[0]
    filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_fam_medical_history)]
    keywords_list = filtered_df['KEYWORD'].tolist()
    selected_fam_medical_history_new = ', '.join(keywords_list)

final_responses['fam_medical'] = selected_fam_medical_history_new
####

# Question 4: Select personal info
st.header("Personal information")
selected_personal_info = st.multiselect("Select and answer the personal information questions applicable to you:", per_quest['Questions'])

# mapping the required keyword
if len(selected_personal_info) == 0:
    selected_personal_info_new = []
else:
    # selected_personal_info_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_personal_info[0]]['KEYWORD'] # .iloc[0]
    filtered_df = df_quest_map[df_quest_map['EVIDENCE'].isin(selected_personal_info)]
    keywords_list = filtered_df['KEYWORD'].tolist()
    selected_personal_info_new = ', '.join(keywords_list)

final_responses['personal'] = selected_personal_info_new

#####################################
# only 1 quest in personal info with dropdown answers
# simple dropdown

selected_question = st.selectbox("Select the applicable personal questions and answer from the dropdown one by one:", list(filtered_per_quest_dict.keys()))

# Display the selected question
# st.write("You selected:", selected_question)

# Create a dropdown for selecting an answer based on the selected question
selected_answer = st.selectbox("Select answer:", filtered_per_quest_dict[selected_question])

# Button to submit the response
if st.button("Submit Response 2"):
    if selected_question != "Select a Question" and selected_answer:
        # Store the response or perform any necessary action
        st.write(f"Question: {selected_question}")
        st.write(f"Answer: {selected_answer}")
        
        # # mapping the required keyword
        # selected_personal_info_new = df_quest_map[df_quest_map['EVIDENCE'] == selected_personal_info]['KEYWORD'].iloc[0]
        # mapping the required keyword
        selected_question = df_quest_map[df_quest_map['EVIDENCE'] == selected_question]['KEYWORD'].iloc[0]

        # You can add code to store responses in a database, file, or any other desired location
        final_responses['personal1'] = {selected_question:selected_answer}



#####################
# getting response in required format for model inference
data = final_responses

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

try:
    # Join the formatted key-value pairs with newlines
    formatted_string = "\n".join(result)
    formatted_string = formatted_string.replace("symptoms_quest is ", "").replace("personal is ", "").replace("medical is ", "").replace("fam_", "")
    new_str = ", ".join(formatted_string.split("\n"))
    final_str = " ".join(new_str.split())
except Exception as e:
    print(e, "----")
    print("all questions are not yet answered")
    final_str = ""

st.write(f"final_response: {final_str}")

# Predictions
st.header("Disease Predictions")

if st.button("Get Predictions"):
    if len(final_str) != 0:
        from predictions import get_predictions
        disease_pred = get_predictions(final_str)

        final_disease_pred = [f'{item[0]}: {item[1]*100:.5f}' for item in disease_pred]

        st.subheader(f"Top 3 disease predictions:")
        for item in final_disease_pred:
            st.write(item)

    else:
        st.write("First fill the entire form and then get predictions")


# Optionally, display the submitted responses
# st.subheader("Submitted Responses")
# You can add code to display stored responses here





###########
# Display selected symptoms and medical history
# st.write("Selected Symptoms:", selected_symptoms)
# st.write("Selected Medical History:", selected_medical_history)
# st.write("Selected Family Medical History:", selected_fam_medical_history)
# st.write("Selected Personal Info:", selected_personal_info)
