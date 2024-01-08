import pandas as pd
import numpy as np
import os
import streamlit as st

BASE_DIR = st.secrets.base_dir
username = st.session_state.username
teamname = st.session_state.teamname

def Evaluate(filename, question_number):

    submitted_resfile = pd.read_csv(filename, sep = ",", header = None)
    question_file = [st.secrets.q1_path,st.secrets.q2_path][question_number - 1]
    actual_resfile = pd.read_csv(question_file, sep = ",", header = None)

    if(len(submitted_resfile.columns) != len(actual_resfile.columns)):
        return -9

    accuracy = 100* (1 - (submitted_resfile[0] - actual_resfile[0]).sum()**2/(actual_resfile[0] + submitted_resfile[0]).sum()**2)
    return accuracy

def calc_uncertainty(metric,sample):
    return np.sqrt((1.0 - metric)/len(sample)) * 100.

def evaluate(filepath, q):
    """
    src code From Kishan Rajput:
    Staff Computer Scientist
    Thomas Jefferson National Accelerator Facility VA USA.

    Modified by:
    Karthik Suresh

    """
    solutions = [st.secrets.q1_path,st.secrets.q2_path]
    label_fileContent = pd.read_csv(solutions[q-1])
    label_fileContent = label_fileContent.apply(pd.to_numeric)
    sorted_labels = label_fileContent.sort_values('eventID')
    sorted_eventID = sorted_labels.eventID.values
    labels = np.array(sorted_labels)[:,1]

    # Handle files with different separators (Allow only comma separated?)
    try:
        content = pd.read_csv(filepath,sep=',',index_col=None)
    except:
        status = "File could not be read..."
        return status, -1,None

    # Check number of columns
    columns = content.columns
    nColumns = len(columns)
    if nColumns != 2:
        status = "Number of Columns not equal to 2. Check example notebook on formatting the result file."
        return status, -1,None

    # Trim the content
    content = content[columns[:2]]
    #content = content[['eventID','PID']]

    if len(content) < labels.shape[0]:
        status = "Not enough predictions provided"
        return status, -1,None

    content = content[:labels.shape[0]]
    #print(content)
    # Convert df to numeric
    try:
        numeric_content = content.apply(pd.to_numeric)
    except:
        status = "Corrupt file"
        return status, -1,None

    # Check for NaNs
    if numeric_content.isnull().values.any():
        status = "File contains NaN"
        return status, -1,None
    if(np.sum(sorted_eventID - numeric_content['eventID'].values) !=0):
        status = "Event IDs do not match"
        return status, -1,None
    predictions = numeric_content.sort_values('eventID').values[:,1]


    frac_correct = np.mean(labels == predictions)
    uncertainty = calc_uncertainty(frac_correct,predictions)
    score = 100.*frac_correct
    status = "Success!"
    #score = 50.0 + 50.0*(frac_correct - threshold)/(1 - threshold)
    return  status,score,uncertainty
