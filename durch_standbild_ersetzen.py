#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import libs and define functions


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


def create_folder(folder_name):
    try:
        # Create a new folder in the current working directory
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")


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


def get_standbild(input_file,output_file,cut_head):
    
    #creat timedelta and add 1 miliseconds
    time_delta = pd.to_timedelta(cut_head)
    new_time_delta = time_delta + pd.Timedelta(milliseconds=1)

    #create dummy for calculation to transform data type back to datetype
    dummy_date = pd.Timestamp('1900-01-01')
    new_timestamp = dummy_date + new_time_delta

    #get the new time back to wished str format
    cut_tail = new_timestamp.strftime('%H:%M:%S.%f')[:-3]

    # Construct the command
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', cut_head,
        '-to', cut_tail,
        '-an', #audio no
        '-c:v', 'libx264', output_file
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


# In[ ]:


def get_audio(input_file,output_file,cut_head,cut_tail):
    
    #Construct command
    command = ['ffmpeg',
               '-i', input_file,
               '-ss', cut_head,
               '-to', cut_tail,
               '-vn','-c:a', 'copy', output_file]
    
    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


# In[ ]:


def merge_audio_and_video(video_file,audio_file,output_file):
    #Construct command
    command = ['ffmpeg',
               '-i', video_file,
               '-i', audio_file,
               '-c:v', 'copy',
               '-c:a', 'copy', output_file
               ]
    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


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


def concatenate_videos(input_file, output_file):
    
    command = [
        'ffmpeg',
        '-f', 'concat', 
        '-i', input_file,
         '-c:v', 'copy',
         '-c:a', 'copy',
        output_file
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("An error occured:", e)


# In[ ]:


# Get file and clean it


# In[ ]:


video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)


# In[ ]:


# Get Standbild


# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        output_file = f"{video_name.split('.')[0]}_standbild.mp4"
        cut_head = video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]

        #building logic when just to cut head or tail
        if cut_head == "nan":
            continue
        print("video_name:",video_name,"cuttime:",cut_head,)
        get_standbild(video_name,output_file,cut_head)
except Exception as error:
    print("An error occurred:", error)


# In[ ]:


# get audio


# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        
        if video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx] == "nan":
            continue
        # timedelta = cut_tail - pd.to_timedelta(cut_head)
        # dummy_date = pd.Timestamp('1900-01-01')
        # new_timestamp = dummy_date + timedelta
        # cut_tail = new_timestamp.strftime('%H:%M:%S.%f')[:-3]

        #Define arguments
        output_file = f"{video_name.split('.')[0]}_head_audio.mp4"
        cut_head = video_schnitt_df["vorne_abschneiden_bis"][idx]
        cut_tail = video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]

        if cut_head == "nan":
            cut_head = "00:00:00"

        print("video_name",video_name,"output_file", output_file,"cut_head",cut_head,"cut_tail:", cut_tail)
        get_audio(video_name,output_file,cut_head,cut_tail)

except Exception as error:
    print("An error occurred:", error)


# In[ ]:


# Cut the original Video


# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx] == "nan":
            continue
        # define arguments
        output_file = f"{video_name.split('.')[0]}_ohne_start_ende_standbild.mp4"
        cut_head = video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]
        cut_tail = video_schnitt_df["hinten_abschneiden_ab"][idx]

        #building logic when just to cut head or tail
        if cut_tail == "nan":
            cut_tail = get_video_duration(video_name)
    
        print("input name:",video_name,"Schnittpunkte:", cut_head, cut_tail)
        cut_head_tail(video_name, output_file, cut_head, cut_tail)
except Exception as error:
    print("An error occurred:", error)


# In[ ]:


#merge audio and video


# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx] == "nan":
            continue
        video_file = f"{video_name.split('.')[0]}_standbild.mp4"
        audio_file = f"{video_name.split('.')[0]}_head_audio.mp4"
        output_file = f"{video_name.split('.')[0]}_merged_start.mp4"
        
        print("video:", video_file, "audio:", audio_file, "output", output_file)
        merge_audio_and_video(video_file,audio_file,output_file)

except Exception as error:
    print("An error occured:", error)


# In[ ]:


# concat to endproduct


# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx] == "nan":
            continue
        
        #define input for the text file with the videos we want to concat
        video1 = f"{video_name.split('.')[0]}_merged_start.mp4"
        video2 = f"{video_name.split('.')[0]}_ohne_start_ende_standbild.mp4"
        textfile_content = f"file '{video1}'\nfile '{video2}'"

        #create the file with content
        with open('dummy.txt', 'w') as textfile:
            textfile.write(textfile_content)

        #define parameters for concat function
        output_file = f"{video_name.split('.')[0]}_endprodukt.mp4"
        textfile_name = "dummy.txt"
        print("file content:", textfile_content)
        concatenate_videos(textfile_name,output_file)
        
except Exception as error:
    print("An error occured:", error)


# In[ ]:


# create folder and move files


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