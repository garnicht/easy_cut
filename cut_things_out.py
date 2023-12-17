#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Import needed libs and define functions


# In[ ]:


import pandas as pd
import subprocess
import os
import shutil


# In[ ]:


def remove_end_in_name(filename):
    splitted = filename.split("_")
    splitted.pop()
    joined_string = "_".join(splitted)
    return joined_string


# In[ ]:


def get_creation_time(file_path):
    try:
        creation_time = os.path.getctime(file_path)
        return pd.to_datetime(creation_time, unit='s')
    except Exception as e:
        print(f"Error getting creation time for {file_path}: {e}")
        return None


# In[ ]:


def get_video_duration(file_path):
    command = ['ffmpeg', '-i', file_path]
    result = subprocess.run(command, text=True, capture_output=True)
    output_lines = result.stderr.split('\n')
    duration_line = [line for line in output_lines if 'Duration' in line][0]
    duration = duration_line.strip().split(",")[0].split(" ")[1]
    return duration


# In[ ]:


def create_folder(folder_name):
    try:
        # Create a new folder in the current working directory
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")


# In[ ]:


def get_the_table_data():
    for f in os.listdir():
        if f.endswith(".csv"):
                video_schnitt_df = pd.read_csv(f)
                print(f"Table {f} loaded succesfully")
                return video_schnitt_df
    raise ValueError("There is no csv in this directory")


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


# # Get the file and clean it

# In[ ]:


video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)


# # remove more slices in a video

# In[ ]:


try:
    # videos need to be in same directory with python script
    trash_list = []
    for idx, video_name in video_schnitt_df["dateiname"].items():
        if not os.path.exists(video_name):
            print("Following file does not exist:",video_name)
            continue
        
        columns_to_cut = ["vorne_abschneiden_bis","rausschneiden_ab","rausschneiden_bis","cut2_ab","cut2_bis","cut3_ab","cut3_bis","cut4_ab","cut4_bis","cut5_ab","cut5_bis","hinten_abschneiden_ab"]

        parts_list = []
        video1 = 0
        video2 = 0
        end_reached = None
        print("Video Name to cut:", video_name)

        try:
            for i,col in enumerate(columns_to_cut):
                cut_head = video_schnitt_df[col][idx]
                cut_tail = video_schnitt_df[columns_to_cut[i+1]][idx]
                print("index:",i,"Column:",col)
                print("Timestamps before changing:",cut_head,cut_tail)

                #logic to handle the nans
                if cut_head == "nan" and cut_tail == "nan" and end_reached == True:
                    end_reached = None
                    print("Break used")
                    break
                if  cut_head == "nan":
                    cut_head = "00:00:00"
                    print("cut_head ersetzt")

                if cut_tail == "nan" and video_schnitt_df["hinten_abschneiden_ab"][idx] == "nan":
                    cut_tail = get_video_duration(video_name)
                    end_reached = True
                if cut_tail == "nan":
                    cut_tail = video_schnitt_df["hinten_abschneiden_ab"][idx]
                    end_reached = True
                    print("hinten abschneiden got")
                output_file = f"{video_name.split('.')[0]}_part{i}.mp4"
                print("Timestamps after changing:",cut_head,cut_tail)
                cut_head_tail(video_name, output_file, cut_head, cut_tail)
                
                if i not in [1, 3, 5, 7, 9, 11]:
                    parts_list.append(output_file)
                else:
                    trash_list.append(output_file)

                if len(parts_list) == 2:
                    video1 = parts_list[0]
                    video2 = parts_list[1]
                    
                    textfile_content = f"file '{video1}'\nfile '{video2}'"

                    #create the file with content
                    with open('dummy.txt', 'w') as textfile:
                        textfile.write(textfile_content)

                    #define parameters for concat function
                    textfile_name = "dummy.txt"

                    output_file = f"{video_name.split('.')[0]}_concatted{i}.mp4"
                    
                    parts_list.clear()
                    parts_list.append(output_file)
                    print(textfile_content, "output:", output_file)
                    concatenate_videos(textfile_name,output_file)                

        except Exception as e:
            print("skip to next video because:",e)

except Exception as error:
    print("An error occured:", error)   


# # rename the right videos to _endprodukt

# In[ ]:


# create a list with videonames of the youngest version that is not in trash list
files = []

for video_name in video_schnitt_df["dateiname"]:
    original_prefix = video_name.split('.')[0]
    youngest_creation_time = None
    youngest_video = None 

    for f in os.listdir():     
        if f.endswith(".mp4") and f not in trash_list:
            if "_" in f:
                part_prefix = remove_end_in_name(f)
            else:
                part_prefix = f.split('.')[0]
            
            if part_prefix == original_prefix:
                creation_time = get_creation_time(f)
                if youngest_creation_time is None or creation_time > youngest_creation_time:
                    youngest_creation_time = creation_time
                    youngest_video = f     
    if youngest_video is not None:
        files.append(youngest_video)    
  
print("All the youngest versions of a video:",files)


# In[ ]:


# create a list of original video_names
original_video_names = list()

for video_name in video_schnitt_df["dateiname"]:
    if video_name != "nan":
        original_video_names.append(video_name)


# In[ ]:


#Compare the filenames with the original Videos
files_to_reaname = [element for element in files if element not in original_video_names]

print("Files that are gonna be renamed:",files_to_reaname)


# In[ ]:


# rename the videos
try:
    for file in files_to_reaname:
        new_name = f"{file.split('.')[0]}_cut_things_out_endprodukt.mp4"
        os.rename(file,new_name)
        print(new_name)
except Exception as e:
    print("Error while renaming:",e)


# # create folders and move files

# In[ ]:


path_folder_endprodukte = "endprodukte"
create_folder(path_folder_endprodukte)

path_folder_script_output = "script_output"
create_folder(path_folder_script_output)


# In[ ]:


for filename in os.listdir():
    if filename.endswith("endprodukt.mp4"):
        shutil.move(filename,path_folder_endprodukte)
    elif filename.endswith("mp4") and filename not in original_video_names:
        shutil.move(filename,path_folder_script_output)

