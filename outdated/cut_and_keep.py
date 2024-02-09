#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import stuff and define functions


# In[ ]:


import pandas as pd
import subprocess
import os
import shutil
import re


# In[ ]:


def get_the_table_data():
    for f in os.listdir():
        if f.endswith(".csv"):
                video_schnitt_df = pd.read_csv(f)
                print(f"Table {f} loaded succesfully")
                return video_schnitt_df
    raise ValueError("There is no csv in this directory")


# In[ ]:


def get_video_duration(file_path):
    command = ['ffmpeg', '-i', file_path]
    result = subprocess.run(command, text=True, capture_output=True)
    output_lines = result.stderr.split('\n')
    duration_line = [line for line in output_lines if 'Duration' in line][0]
    duration = duration_line.strip().split(",")[0].split(" ")[1]
    return duration


# In[ ]:


def clean_the_data(df):
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.strip()
    df = df.astype(str)
    print("Table Columns cleaned")
    return df


# In[ ]:


def cut_head_tail(original_video,output_file,cut_head="00:00:00",cut_tail="00:50:00"):

    # Construct the command
    command = [
        'ffmpeg',
        '-i', original_video,
        '-ss', cut_head,
        '-to', cut_tail,
        '-c:v','libx264',
        '-c:a', 'copy',
        output_file
    ]
    
     # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


# In[ ]:


def create_folder(folder_name):
    try:
        # Create a new folder in the current working directory
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")


# In[ ]:


def cut_in_2_pieces(input_file, timestamp, head_output, tail_output):
    
    # -ss = ab dort; -to = bis dort
    head_cmd = ['ffmpeg', '-i', input_file, '-to', timestamp, '-c:v', 'libx264', '-c:a', 'copy', head_output]
    tail_cmd = ['ffmpeg', '-i', input_file, '-ss', timestamp, '-c:v', 'libx264', '-c:a', 'copy', tail_output]

# Execute the commands
    try:
        subprocess.run(head_cmd, check=True)
        subprocess.run(tail_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


# In[ ]:


def get_columns_to_divide(df):
    pattern = re.compile(r'^teilen\d+_[a-z]+$')
    dummy = []
    for column in df.columns:
        if pattern.match(column):
            dummy.append(column)
    return dummy


# In[ ]:


def calculate_time(*timestamps,kind="addition"):
    """
    Calculate time based on the given timestamps and operation type.

    Parameters:
    - timestamps (str): Variable number of timestamps.
    - kind (str): The operation type. Allowed values are 'addition' and 'subtraction'.
    """
    
    #addition
    if kind == "addition":
        stamp1 = None
        for timestamp in timestamps:
        
        # calculate timestamp
            if stamp1 is None:
                stamp1 = timestamp

            else:
                timedelta = stamp1 + pd.to_timedelta(timestamp)
                dummy_date = pd.Timestamp('1900-01-01')
                new_timestamp = dummy_date + timedelta
                timestamp = new_timestamp.strftime('%H:%M:%S.%f')[:-3]
                return timestamp
    
    #subtraction
    elif kind == "subtraction":
        stamp1 = None
        for timestamp in timestamps:
        
        # calculate timestamp
            if stamp1 is None:
                stamp1 = timestamp

            else:
                timedelta = stamp1 - pd.to_timedelta(timestamp)
                dummy_date = pd.Timestamp('1900-01-01')
                new_timestamp = dummy_date + timedelta
                timestamp = new_timestamp.strftime('%H:%M:%S.%f')[:-3]
                return timestamp        


# In[ ]:


# get file and clean


# In[ ]:


video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)


# In[ ]:


# cut and keep the pieces


# In[ ]:


#loop through videonames and then through columns to divide
for row, video_name in video_schnitt_df["dateiname"].items():
    columns_to_divide = get_columns_to_divide(video_schnitt_df)
    for col_num,col in enumerate(video_schnitt_df[columns_to_divide]):
        
        #rule when there is more then one division
        if video_schnitt_df[col][row] != "nan":
            if col_num > 0:
                input_file = f"{video_name.split('.')[0]}_tail{col_num}.mp4"
                timestamp1 = video_schnitt_df[columns_to_divide[col_num -1]][row]
                timestamp2 = video_schnitt_df[col][row]
                timestamp = calculate_time(timestamp2,timestamp1,kind="subtraction")
                head_output = f"{video_name.split('.')[0]}_mitte{col_num+ 1}.mp4"
                tail_output = f"{video_name.split('.')[0]}_tail{col_num +1}.mp4"
                print("PRINT: timestamps before calculation:",timestamp1,timestamp2)
                print("PRINT: all Variables further cut:",input_file,timestamp,head_output,tail_output)

                cut_in_2_pieces(input_file,timestamp,head_output,tail_output)
                os.remove(input_file)
            else:

                #define all variables needed
                input_file = video_name
                timestamp = video_schnitt_df[col][row]
                head_output = f"{video_name.split('.')[0]}_head{col_num +1}.mp4"
                tail_output = f"{video_name.split('.')[0]}_tail{col_num +1}.mp4"
                
                print("all variables:",input_file,timestamp,head_output,tail_output)

                #start seperation
                cut_in_2_pieces(input_file,timestamp,head_output,tail_output)


# In[ ]:


# create folders and move files


# In[ ]:


path_folder_endprodukte = "endprodukte"
create_folder(path_folder_endprodukte)

path_folder_script_output = "script_output"
create_folder(path_folder_script_output)


# In[ ]:


original_video_names = list()

for video_name in video_schnitt_df["dateiname"]:
    if video_name != "nan":
        original_video_names.append(video_name)


# In[ ]:


for filename in os.listdir():
    if filename.endswith("mp4") and filename not in original_video_names:
        shutil.move(filename,path_folder_endprodukte)

