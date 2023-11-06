import pandas as pd
import torch
import pickle
from transformers import AutoTokenizer, AutoModel
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st



@st.cache_resource
def load_model_tok(model_name):
    if model_name == "bert":
        # st.write("Model_Selected: bert")

        sef = open("symptoms_clinicalbert_embeddings_49_PD.pkl", 'rb')
        symptom_embeddings = pickle.load(sef)
        # Load a ClinicalBERT model and tokenizer. Need to cache it on streamlit.
        tokenizer = AutoTokenizer.from_pretrained("medicalai/ClinicalBERT")
        model = AutoModel.from_pretrained("medicalai/ClinicalBERT")
        
    elif model_name == "all_mini":
        # st.write("Model_Selected: all_mini")

        sef = open("symptoms_format_new_v1_allMiniLM_embeddings_49_PD.pkl", 'rb')
        symptom_embeddings = pickle.load(sef)
        tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    
    return symptom_embeddings, tokenizer, model
# tokenizer, model = load_model_tok()

# Define a test symptom description for classification
# test_symptoms = "shortness of breath or difficulty breathing , pain characteristics are burning, pain location is pharynx, side of the chest(R), have chronic obstructive pulmonary disease (COPD) , cough , nasal congestion or runny nose , feels pain , pain radiates to nowhere, wheezing sound while exhaling , 5.0, preciseness in pain location is 7.0 "

def get_predictions(test_symptoms, model_name):
    symptom_embeddings, tokenizer, model = load_model_tok(model_name)
    # Calculate the average embedding for the test symptom description
    test_inputs = tokenizer(test_symptoms, return_tensors="pt", padding=True)#, truncation=True)
    with torch.no_grad():
        test_outputs = model(**test_inputs)
        test_embedding = torch.mean(test_outputs.last_hidden_state, dim=1).numpy()

    #test_embedding

    # Calculate the cosine similarity between the test symptom and each disease
    similarities = {}
    for disease, embedding in symptom_embeddings.items():
        similarity = cosine_similarity(test_embedding, embedding)[0][0]
        similarities[disease] = similarity

    # Classify the disease with the highest similarity
    predicted_disease = max(similarities, key=similarities.get)
    #print("Predicted Disease:", predicted_disease)

    similarities_sorted = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    result = similarities_sorted[:3]
    
    return result