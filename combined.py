#!/usr/bin/env python
# coding: utf-8

# # Import libs and define functions

# In[ ]:


import pandas as pd
import subprocess
import os
import shutil
import re
import sys 


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
        '-c:v','libx264', #libx264 to encode and copy to test
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
        '-c:v', 'libx264', output_file # libx264 to encode and copy to test (but that didnt work the last time)
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
               '-vn',
               '-c:a', 'copy', output_file]
    
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


def get_columns_to_cut(df):
    pattern = re.compile(r'^rausschneiden\d+_[a-z]+$')
    dummy = []
    for column in df.columns:
        if pattern.match(column):
            dummy.append(column)
    return dummy


# In[ ]:


def get_list_of_evens(input_list):
    dummy = []
    for i in range(len(input_list)):
        if i % 2 == 0:
            dummy.append(i)
    return dummy


# In[ ]:


def concatenate_videos(input_file, output_file):
    
    command = [
        'ffmpeg',
        '-f', 'concat', 
        '-i', input_file,
         '-c:v', 'copy', #libx264 to encode if needed
         '-c:a', 'copy',
        output_file
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("An error occured:", e)


# In[ ]:


def check_for_non_zero_digit(string):
    # Define a regular expression pattern to match any digit other than 0
    pattern = re.compile('[1-9]')

    if pattern.search(string):
        return True       
    else:
        return False


# In[ ]:


def extract_data_from_row(df,row_index,columns):
    dic = df.loc[row_index,columns].to_dict()

    return dic


# In[ ]:


def check_special_case(df):
    columns = get_columns_to_cut(video_schnitt_df)
    for idx, video_name in df["dateiname"].items():
        data = video_schnitt_df["rausschneiden1_ab"][idx]
        if check_for_non_zero_digit(data) == True:
            dic = extract_data_from_row(df,idx,columns)
            counter = 0
            for key,value in dic.items():
                if value == "nan":
                    counter += 1
            if counter < 2:
                print(f"""Error because in row of {video_name}
we need to have at least 2 free 'rausschneiden...' columns 
to execute the code. Please change the csv as needed and
restart the script""")
                sys.exit("Script terminated due to error.")


# In[ ]:


def solve_special_case(df):
    
    for idx,video_name in df["dateiname"].items():
        
        if check_for_non_zero_digit(df["rausschneiden1_ab"][idx]) == False:
            continue

        else:
            columns = get_columns_to_cut(df)
            dic = extract_data_from_row(df,idx,columns)
            dummy = []
            counter = 0

            # put values from row into list and change first two columns to 000000
            for key, value in dic.items():
                if value != "nan":
                    dummy.append(value)
                if counter < 2:
                    dic[key] = "00:00:00"
                    counter += 1
        # fülle das jeweilige dic solange mit daten bis liste leer
        for key, value in dic.items():
            if value != "00:00:00" and dummy:
                dic[key] = dummy.pop(0)
        
        for key, value in dic.items():
            df.loc[idx, key] = value
    
    return df


# # Get file and clean it

# In[ ]:


video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)


# # Check Special Cases and input error

# In[ ]:


check_special_case(video_schnitt_df)


# In[ ]:


solve_special_case(video_schnitt_df)


# # Get Standbild

# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        
        if video_schnitt_df["standbild_bis"][idx] == "nan":
            continue
        else:
            cut_head = video_schnitt_df["standbild_bis"][idx]
        
        output_file = f"{video_name.split('.')[0]}_standbild.mp4"

        print("video_name:",video_name,"cuttime:",cut_head,)
        get_standbild(video_name,output_file,cut_head)
except Exception as error:
    print("An error occurred:", error)


# # Get audio

# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        
        if video_schnitt_df["standbild_bis"][idx] == "nan":
            continue

        #Define arguments
        output_file = f"{video_name.split('.')[0]}_head_audio.mp4"
        cut_head = "00:00:00"
        cut_tail = video_schnitt_df["standbild_bis"][idx]

        print("video_name",video_name,"output_file", output_file,"cut_head",cut_head,"cut_tail:", cut_tail)
        get_audio(video_name,output_file,cut_head,cut_tail)

except Exception as error:
    print("An error occurred:", error)


# # Cut head of the original Video

# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["standbild_bis"][idx] == "nan":
            continue
        
        # define arguments
        cut_head = video_schnitt_df["standbild_bis"][idx]
        cut_tail = get_video_duration(video_name)
        output_file = f"{video_name.split('.')[0]}_ohne_start_standbild.mp4"
    
        print("input name:",video_name,"Schnittpunkte:", cut_head, cut_tail)
        cut_head_tail(video_name, output_file, cut_head, cut_tail)
except Exception as error:
    print("An error occurred:", error)


# # Merge audio and video

# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["standbild_bis"][idx] == "nan":
            continue
        
        video_file = f"{video_name.split('.')[0]}_standbild.mp4"
        audio_file = f"{video_name.split('.')[0]}_head_audio.mp4"
        output_file = f"{video_name.split('.')[0]}_merged_start.mp4"
        
        print("video:", video_file, "audio:", audio_file, "output", output_file)
        merge_audio_and_video(video_file,audio_file,output_file)

except Exception as error:
    print("An error occured:", error)


# # Concat to endproduct

# In[ ]:


try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if video_schnitt_df["standbild_bis"][idx] == "nan":
            continue
        
        #define input for the text file with the videos we want to concat
        video1 = f"{video_name.split('.')[0]}_merged_start.mp4"
        video2 = f"{video_name.split('.')[0]}_ohne_start_standbild.mp4"
        textfile_content = f"file '{video1}'\nfile '{video2}'"

        #create the file with content
        with open('dummy.txt', 'w') as textfile:
            textfile.write(textfile_content)

        #define parameters for concat function
        output_file = f"{video_name.split('.')[0]}_standbild_endprodukt.mp4"
        textfile_name = "dummy.txt"
        print("file content:", textfile_content)
        concatenate_videos(textfile_name,output_file)
        
except Exception as error:
    print("An error occured:", error)


# # Create folder and move files

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


# # Start to cut things out

# In[ ]:


# cut all the videos that did not use the standbild ersetzen script
try:
    # videos need to be in same directory with python script
    trash_list = []
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if not os.path.exists(video_name):
            print("Following file does not exist:",video_name)
            continue

        #check ob video schon standbid ersetzt bekommen, use other videoname
        if video_schnitt_df["standbild_bis"][idx] != "nan":
            print(video_name,"skipped because other video in endprodukte needs to be used")
            continue

        columns_to_cut = get_columns_to_cut(video_schnitt_df)
        evens = get_list_of_evens(columns_to_cut)

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
                
                if cut_head != "nan" and cut_head != "00:00:00" and i == 0:
                    print("Skipped because of special case")
                    
                    break
                
                if cut_head == "nan" and cut_tail == "nan":
                    print("Break used")
                    break
                
                if end_reached == True:
                    break

                if  cut_head == "nan":
                    cut_head = "00:00:00"
                    print("cut_head ersetzt")

                if cut_tail == "nan":
                    cut_tail = get_video_duration(video_name)
                    end_reached = True
                    print("end reached")
                    
                output_file = f"{video_name.split('.')[0]}_part{i}.mp4"
                print("Timestamps after changing:",cut_head,cut_tail)
                cut_head_tail(video_name, output_file, cut_head, cut_tail)
                
                if i not in evens:
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


# ## cut all the videos that did not use the standbild ersetzen script
# 

# In[ ]:


try:
    # videos need to be in same directory with python script
    trash_list = []
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if not os.path.exists(video_name):
            print("Following file does not exist:",video_name)
            continue

        #check ob video schon standbid ersetzt bekommen, use other videoname
        if video_schnitt_df["standbild_bis"][idx] == "nan":
            print(f"skipped this {video_name} because it is already finished")
            continue
        
        folder_name = "endprodukte/"
        new_video_name = folder_name + f"{video_name.split('.')[0]}_standbild_endprodukt.mp4"

        columns_to_cut = get_columns_to_cut(video_schnitt_df)
        evens = get_list_of_evens(columns_to_cut)

        parts_list = []
        video1 = 0
        video2 = 0
        end_reached = None
        print("Video Name to cut:", video_name, "actual input to cut:", new_video_name)

        try:
            for i,col in enumerate(columns_to_cut):
                cut_head = video_schnitt_df[col][idx]
                cut_tail = video_schnitt_df[columns_to_cut[i+1]][idx]
                print("index:",i,"Column:",col)
                print("Timestamps before changing:",cut_head,cut_tail)

                #logic to handle the nans
                if cut_head != "nan" and cut_head != "00:00:00" and i == 0:
                    print("Skipped because of special case")
                    break
                
                if cut_head == "nan" and cut_tail == "nan":
                    print("Break used")
                    break
                
                if end_reached == True:
                    print("Break used")
                    break

                if  cut_head == "nan":
                    cut_head = "00:00:00"
                    print("cut_head ersetzt")

                if cut_tail == "nan":
                    cut_tail = get_video_duration(video_name)
                    end_reached = True
                    print("end reached")
                    
                output_file = f"{video_name.split('.')[0]}_part{i}.mp4"
                print("Timestamps after changing:",cut_head,cut_tail)
                cut_head_tail(new_video_name, output_file, cut_head, cut_tail)
                
                if i not in evens:
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


# # Rename the right videos to _endprodukt

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


# # Move files

# In[ ]:


for filename in os.listdir():
    if filename.endswith("endprodukt.mp4"):
        shutil.move(filename,path_folder_endprodukte)
    elif filename.endswith("mp4") and filename not in original_video_names:
        shutil.move(filename,path_folder_script_output)


# # Delete old endproducts

# In[ ]:


# create a list with videonames of the youngest version that is not in trash list
files = []

for video_name in video_schnitt_df["dateiname"]:
    original_prefix = video_name.split('.')[0]
    youngest_creation_time = None
    youngest_video = None 
    pattern = re.compile(rf'^{re.escape(original_prefix)}_(concatted\d+|standbild).*$')

    for f in os.listdir("endprodukte/"):     
        
        if pattern.match(f):
            #print(pattern, "matches", f)
            creation_time = get_creation_time("endprodukte/"+f)
            if youngest_creation_time is None or creation_time > youngest_creation_time:
                youngest_creation_time = creation_time
                youngest_video = f     
    if youngest_video is not None:
        files.append(youngest_video)    
  
print("All the youngest versions of a video:",files)


# In[ ]:


remove_list = []

for f in os.listdir("endprodukte/"):     
    if f not in files:
        remove_list.append(f)

print(remove_list)


# In[ ]:


for i in remove_list:
    os.remove("endprodukte/" + i)

