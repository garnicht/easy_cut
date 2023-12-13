#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import stuff and define functions


# In[ ]:


import pandas as pd
import subprocess
import os
import shutil


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


# maybe needs to be encoded too! 

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


# get file and clean


# In[ ]:


video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)


# In[ ]:


# cut the video first if needed


# In[ ]:


# videos need to be in same directory with python script
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["schnitt_setzen_bei"][idx] == "nan":
            continue

        # define arguments
        output_file = f"{video_name.split('.')[0]}_ohne_start_ende_cut_and_keep.mp4"
        cut_head = video_schnitt_df["vorne_abschneiden_bis"][idx]
        cut_tail = video_schnitt_df["hinten_abschneiden_ab"][idx]

        #building logic when just to cut head or tail
        if cut_head == "nan":
            cut_head = "00:00:00"
        if cut_tail == "nan":
            cut_tail = get_video_duration(video_name)
    
        print("input name:",video_name,"Schnittpunkte:", cut_head, cut_tail)
        cut_head_tail(video_name, output_file, cut_head, cut_tail)
except Exception as error:
    print("An error occurred:", error)


# In[ ]:


# cut and keep the pieces


# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        
        if video_schnitt_df["schnitt_setzen_bei"][idx] == "nan":
            continue

        head_output = f"{video_name.split('.')[0]}_head_endprodukt.mp4"
        tail_output = f"{video_name.split('.')[0]}_tail_endprodukt.mp4"

        # calculate timestamp
        timedelta = video_schnitt_df["schnitt_setzen_bei"][idx] - pd.to_timedelta(video_schnitt_df["vorne_abschneiden_bis"][idx])
        dummy_date = pd.Timestamp('1900-01-01')
        new_timestamp = dummy_date + timedelta
        timestamp = new_timestamp.strftime('%H:%M:%S.%f')[:-3]

        input_file = f"{video_name.split('.')[0]}_ohne_start_ende_cut_and_keep.mp4"
        
        print("input:", input_file, "stamp",timestamp)
        cut_in_2_pieces(input_file,timestamp,head_output,tail_output)

except Exception as error:
    print("An error occurred:", error)


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
    if filename.endswith("endprodukt.mp4"):
        shutil.move(filename,path_folder_endprodukte)
    elif filename.endswith("mp4") and filename not in original_video_names:
        shutil.move(filename,path_folder_script_output)

