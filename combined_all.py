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


def get_columns_to_pause(df):
    pattern = re.compile(r'^pause\d+_[a-z]+$')
    dummy = []
    for column in df.columns:
        if pattern.match(column):
            dummy.append(column)
    return dummy


# In[ ]:


def create_silent_audio(duration, output_file):
    # Command to create silent audio with ffmpeg
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
        '-t', duration,
        '-c:a', 'aac',
        '-b:a', '191k',
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Silent audio file {output_file} created successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating silent audio file: {e}")


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
               '-c:v', 'libx264', # needs to stay libx264
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
        '-i', input_file, # txt file
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


def check_number_of_columns(df):
    columns = get_columns_to_cut(df)
    for row, video_name in df["dateiname"].items():
        data = df["rausschneiden1_bis"][row]
        
        if data != "nan":
            dic = extract_data_from_row(df,row,columns)
            counter = 0

            for key, value in dic.items():
                
                if (key != "rausschneiden1_ab"
                        and value == "nan"):
                    counter += 1
            
            if counter < 3:
                error_message = (
                    f"Error: Insufficient 'rausschneiden...' columns in row of Normalverteilung.mp4.\n"
                    "At least 3 free 'rausschneiden...' columns at the end are required to execute the code.\n"
                    "Please update the CSV file accordingly and restart the script."
                )
                
                print(error_message)
                
                sys.exit("Script terminated due to error.")



# In[ ]:


# def check_special_case(df):
#     columns = get_columns_to_cut(df)
#     for idx, video_name in df["dateiname"].items():
#         data = df["rausschneiden1_ab"][idx]
#         if check_for_non_zero_digit(data) == True:
#             dic = extract_data_from_row(df,idx,columns)
#             counter = 0
#             for key,value in dic.items():
#                 if value == "nan":
#                     counter += 1
#             if counter < 2:
#                 print(f"""Error: Insufficient 'rausschneiden...' columns in row of {video_name}.\n
#                       "At least 2 free 'rausschneiden...' columns at the end are required to execute the code.\n"
#                       "Please update the CSV file accordingly and restart the script.""")
                
#                 sys.exit("Script terminated due to error.")


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


# In[ ]:


def convert_timestamp_to_right_format(input):
    if input != "nan":
        input = pd.to_timedelta(input)
        dummy_date = pd.Timestamp('1900-01-01')
        new_timestamp = dummy_date + input
        new_timestamp = new_timestamp.strftime('%H:%M:%S.%f')[:-3]
        return str(new_timestamp)


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
            if timestamp == "nan":
                timestamp = "00:00:00"
        
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
            if timestamp == "nan":
                timestamp = "00:00:00"        

        # calculate timestamp
            if stamp1 is None:
                stamp1 = timestamp

            else:
                timedelta = stamp1 - pd.to_timedelta(timestamp)
                dummy_date = pd.Timestamp('1900-01-01')
                new_timestamp = dummy_date + timedelta
                new_timestamp = new_timestamp.strftime('%H:%M:%S.%f')[:-3]
                if new_timestamp == '00:00:00.000':
                    new_timestamp = stamp1
                return new_timestamp        


# In[ ]:


def cut_in_2_pieces(input_file, timestamp, head_output, tail_output):
    
    # -ss = ab dort; -to = bis dort
    head_cmd = ['ffmpeg', '-i', input_file, '-to', timestamp, '-c:v', 'libx264', '-c:a', 'copy', head_output] # "-c:v" -> "libx264" to encrypt or "copy" to test
    tail_cmd = ['ffmpeg', '-i', input_file, '-ss', timestamp, '-c:v', 'libx264', '-c:a', 'copy', tail_output] # "-c:v" -> "libx264" to encrypt or "copy" to test

# Execute the commands
    try:
        subprocess.run(head_cmd, check=True)
        subprocess.run(tail_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


# In[ ]:


def calculate_timestamp(col, row):

    input_timestamp = video_schnitt_df[col][row]

    # get diff from cutted videos and subtract
    diff_with_cuts = calculate_time_diff(input_timestamp, row, kind="diff_with_cuts")
    new_timestamp = calculate_time(input_timestamp, diff_with_cuts, kind="subtraction")

    # get diff from pauses and add
    diff_with_pauses = calculate_time_diff(input_timestamp, row, kind="diff_with_pauses")
    new_timestamp = calculate_time(new_timestamp, diff_with_pauses, kind="addition")

    return new_timestamp


# In[ ]:


def calculate_time_diff(input_timestamp,row_number,kind):
    """
    Calculate new timestamp based on the original timestamp and operation type.

    Parameters:
    - timestamp (str): any Input Timestamp
    - kind (str): The operation type. Allowed values are 'diff_with_cuts' and 'diff_with_pauses'.
    - row (int): rownumber of data in dataframe
    """    

    if kind == "diff_with_cuts":
        columns_to_cut = get_columns_to_cut(video_schnitt_df)
        pattern = re.compile(r'^rausschneiden\d+_bis$')
        result = "00:00:00"
        input_timestamp = convert_timestamp_to_right_format(input_timestamp)

        for col_num,col in enumerate(video_schnitt_df[columns_to_cut]):
            
            ab_timestamp = video_schnitt_df[columns_to_cut].iloc[row_number, col_num-1]
            bis_timestamp = video_schnitt_df[col][row_number]
            bis_timestamp = convert_timestamp_to_right_format(bis_timestamp)

            # check wether the timestamp in 'rausschneidenX_bis' is smaller than input
            if pattern.match(col):
                if bis_timestamp != "nan" and str(bis_timestamp) < str(input_timestamp):
                    # print(video_name, "col name:", col)
                    # print("bis timestamp:", bis_timestamp, "ist kleiner als input Tiestamp:",input_timestamp)
                    # print("ab Timestamp ist:", ab_timestamp)
                    # print("bis Timestamp:",bis_timestamp,"minus",ab_timestamp)
                    diff = calculate_time(bis_timestamp,ab_timestamp,kind="subtraction")
                    result = calculate_time(result,diff,kind="addition")
                    # print("Differenz:",diff,"Summe:",result)
                    
        return result

    if kind == "diff_with_pauses":
        columns_to_pause = get_columns_to_pause(video_schnitt_df)
        pattern = re.compile(r'^pause\d+_bei$')
        result = "00:00:00"
        input_timestamp = convert_timestamp_to_right_format(input_timestamp)


        for col_num,col in enumerate(video_schnitt_df[columns_to_pause]):
            
            ab_timestamp = video_schnitt_df[columns_to_pause].iloc[row_number, col_num]
            ab_timestamp = convert_timestamp_to_right_format(ab_timestamp)
            
            try:
                dauer_timestamp = video_schnitt_df[columns_to_pause].iloc[row_number, col_num+1]
            except Exception as e:
                print(e)

            # check wether the timestamp in 'rausschneidenX_bis' is smaller than input
            if pattern.match(col):
                if str(ab_timestamp) < str(input_timestamp):
                    # print(video_name, "col name:", col)
                    # print("ab timestamp:", ab_timestamp, "ist kleiner als input Tiestamp:",input_timestamp)
                    # print("dauer zum adden ist:", dauer_timestamp)
                    result = calculate_time(result,dauer_timestamp,"addition")
                    # print("Summe:",result)  

        return result      


# In[ ]:


def remove_parts(video_name):
    original_prefix = video_name.split('.')[0]
    pattern = re.compile(rf'^{re.escape(original_prefix)}_part\d+.*$')

    for f in os.listdir():
        if f.endswith(".mp4") and pattern.match(f):
            os.remove(f)


# In[ ]:


def rename_part1_videos():
    """This function is a quick solution to solve following problem:
    If a video just needs one cut, and its no special case, then there will be 3 parts and just one will be odd. 
    That means there is no concatted, and that means the part1 video needs to be moved"""

    for video_name in video_schnitt_df["dateiname"]:
        original_prefix = video_name.split('.')[0]
        suffix = "_part1.mp4"
        pattern = re.compile(rf'^{re.escape(original_prefix)}_part\d+.*$')
        counter = 0
        #print("new loop")

        for f in os.listdir():
            if f.endswith(".mp4") and pattern.match(f):
                counter += 1
                if counter > 1:
                    #print("video name:", video_name, "prefix:", original_prefix)
                    #print("file to remove:", original_prefix + suffix, "endfile:", original_prefix + '_concatted1.mp4')
                    os.rename(original_prefix + suffix, original_prefix + "_concatted1.mp4")
                    break


# In[ ]:


# def convert_to_time(input_string):
#     try:
#         time_type = pd.to_datetime(input_string, format='%H:%M:%S.%f').dt.time
        
#         # Get the format
#         formatted_time = time_type.dt.strftime('%H:%M:%S.%f')
#         return formatted_time
#     except ValueError:
#         print("Input string is not in the correct format.")
#         return None


# # Get file and clean it

# In[ ]:


video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)
                    


# # Check Special Cases and input error

# In[ ]:


check_number_of_columns(video_schnitt_df)


# In[ ]:


solve_special_case(video_schnitt_df)


# In[ ]:


# solve special pause at beginning case. script doesnt work when pause ist set at 00:00:00

video_schnitt_df.loc[video_schnitt_df["pause1_bei"] == '00:00:00', "pause1_bei"] = '00:00:00.001'


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
                print("Timestamps after changing:",cut_head,cut_tail, "output file:", output_file)
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
                    remove_parts(video_name)            

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
                    remove_parts(video_name)
                    
        except Exception as e:
            print("skip to next video because:",e)

except Exception as error:
    print("An error occured:", error)   


# # Handle the video outputs

# In[ ]:


rename_part1_videos()


# In[ ]:


# erstmal rausgenommen, kopiert und unten erweitert
# # create a list with videonames of the youngest version that is not in trash list
# files = []

# for video_name in video_schnitt_df["dateiname"]:
#     original_prefix = video_name.split('.')[0]
#     youngest_creation_time = None
#     youngest_video = None 
#     pattern = re.compile(rf'^{re.escape(original_prefix)}_part\d+.*$')


#     for f in os.listdir():     
#         if f.endswith(".mp4") and f not in trash_list and not pattern.match(f):
#             if "_" in f:
#                 part_prefix = remove_end_in_name(f)
#                 print(part_prefix)
#             else:
#                 part_prefix = f.split('.')[0]
            
#             if part_prefix == original_prefix:
#                 creation_time = get_creation_time(f)
#                 if youngest_creation_time is None or creation_time > youngest_creation_time:
#                     youngest_creation_time = creation_time
#                     youngest_video = f     
#     if youngest_video is not None:
#         files.append(youngest_video)    
  
# print("All the youngest versions of a video:",files)


# In[ ]:


# create a list with videonames of the youngest version that is not in trash list
files = []

for video_name in video_schnitt_df["dateiname"]:
    original_prefix = video_name.split('.')[0]
    youngest_creation_time = None
    youngest_video = None 
    pattern = re.compile(rf'^{re.escape(original_prefix)}_concatted\d+.*$')


    for f in os.listdir():     
        if f.endswith(".mp4") and f not in trash_list and pattern.match(f):
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
    print(pattern)
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


# In[ ]:


folder_path = "endprodukte/"

for video_name in video_schnitt_df["dateiname"]:
    original_prefix = video_name.split('.')[0]
    pattern = re.compile(rf'^{re.escape(original_prefix)}_(concatted\d+|standbild).*$')
    
    for f in os.listdir(folder_path):
        if pattern.match(f):
            new_name = folder_path + original_prefix + ".mp4"
            os.rename(folder_path + f,new_name)


# # Start insert_pauses script

# In[ ]:


columns_to_pause = get_columns_to_pause(video_schnitt_df)


# In[ ]:


# get stanbilder
for row, video_name in video_schnitt_df[["dateiname"] + columns_to_pause].query("pause1_bei != 'nan'")["dateiname"].items():
    counter = 1
    
    for idx, col in enumerate(columns_to_pause):
        if video_schnitt_df[col][row] == "nan" or "dauer" in col:
            continue
        output = f"{video_name.split('.')[0]}_stanbild{counter}.mp4"
        timestamp = video_schnitt_df[col][row]

        try:
            print(video_name, "standbild bei:", timestamp, "output:", output)
            get_standbild(video_name,output,timestamp)
        except Exception as e:
            print(e)
        
        counter += 1


# In[ ]:


# get audios with silence for duration
for row, video_name in video_schnitt_df[["dateiname"] + columns_to_pause].query("pause1_bei != 'nan'")["dateiname"].items():
    counter = 1
    
    for idx, col in enumerate(columns_to_pause):
        if video_schnitt_df[col][row] == "nan" or "bei" in col:
            continue
        
        output = f"{video_name.split('.')[0]}_audio{counter}.mp4"
        timestamp = video_schnitt_df[col][row]
        
        try:
            print(video_name, "silence for:", timestamp, "output:", output)
            create_silent_audio(timestamp,output)
        except Exception as e:
            print(e)

        counter += 1


# In[ ]:


# merge all the files
for row, video_name in video_schnitt_df[["dateiname"] + columns_to_pause].query("pause1_bei != 'nan'")["dateiname"].items():
    counter = 1
    
    for idx, col in enumerate(columns_to_pause):
        if video_schnitt_df[col][row] == "nan" or "bei" in col:
            continue
        
        video_file = f"{video_name.split('.')[0]}_stanbild{counter}.mp4"
        audio_file = f"{video_name.split('.')[0]}_audio{counter}.mp4"
        output_file = f"{video_name.split('.')[0]}_pause{counter}.mp4"
        try :
            print(video_name,audio_file,output_file)
            merge_audio_and_video(video_file,audio_file,output_file)
        except Exception as e:
            print(e)
            
        counter += 1


# ## Handle output 

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


# move pauses
try:
    for video_name in video_schnitt_df["dateiname"]:
        original_prefix = video_name.split('.')[0]
        pattern = re.compile(rf'^{re.escape(original_prefix)}_pause\d+.*$')
        
        for f in os.listdir():
            if pattern.match(f):
                print(f, "moved to:", path_folder_endprodukte)
                shutil.move(f,path_folder_endprodukte)
            #elif f.endswith(".mp4") and f not in original_video_names:
                #os.remove(f)

except Exception as e:
    print(e, "or this file already has been removed")


# In[ ]:


# delete byproducts
try:
    for video_name in video_schnitt_df["dateiname"]:
        
        for f in os.listdir():
            if f.endswith(".mp4") and f not in original_video_names:
                os.remove(f)

except Exception as e:
    print(e, "or this file already has been removed")


# ## Cut videos into pieces and concat with pauses

# In[ ]:


# INPUT FILE NEEDS TO BE Adjusted. maybe better file handling before?
# Right now it just checks wether original video is in dir but it or sure is. 

folder_path = "endprodukte/"
versions_to_concat = {}

try:
    for row, video_name in video_schnitt_df[["dateiname"] + columns_to_pause].query("pause1_bei != 'nan'")["dateiname"].items():
        counter = 1
        columns_to_pause = get_columns_to_pause(video_schnitt_df)
        for col_num, col in enumerate(video_schnitt_df[columns_to_pause]):
            
            if "bei" in col and video_schnitt_df[col][row] != "nan":
                
                # Start bei mindestens einer Teilung
                if counter == 1:

                    # define all variables needed
                    if os.path.exists(folder_path + video_name):
                        input_file = folder_path + video_name
                    else:
                        input_file = video_name

                    # timestamp pauses dont have to be added!               
                    original_timestamp = video_schnitt_df[col][row]

                    # get diff from cutted videos and subtract
                    diff_with_cuts = calculate_time_diff(original_timestamp, row, kind="diff_with_cuts")
                    new_timestamp = calculate_time(original_timestamp, diff_with_cuts, kind="subtraction")

                    head_output = f"{video_name.split('.')[0]}_head{counter}.mp4"
                    tail_output = f"{video_name.split('.')[0]}_tail{counter}.mp4"
                    
                    print("all variables:",input_file,new_timestamp,head_output,tail_output)

                    #start separation
                    cut_in_2_pieces(input_file,new_timestamp,head_output,tail_output)
                    
                    versions_to_concat[video_name] = [head_output,f"{folder_path}{video_name.split('.')[0]}_pause{counter}.mp4",tail_output]
                    
                    counter += 1
                
                else:

                    # define alle the vars
                    input_file = f"{video_name.split('.')[0]}_tail{counter-1}.mp4"

                    # timestamp
                    
                    timestamp_previous_iteration = video_schnitt_df[columns_to_pause[col_num-2]][row]
                    diff_with_cuts = calculate_time_diff(timestamp_previous_iteration, row, kind="diff_with_cuts")
                    timestamp_previous_iteration = calculate_time(timestamp_previous_iteration, diff_with_cuts, kind="subtraction")
                    
                    timestamp_current_iteration = video_schnitt_df[col][row]
                    diff_with_cuts = calculate_time_diff(timestamp_current_iteration, row, kind="diff_with_cuts")
                    timestamp_current_iteration = calculate_time(timestamp_current_iteration, diff_with_cuts, kind="subtraction")                   

                    new_timestamp = calculate_time(timestamp_current_iteration, timestamp_previous_iteration, kind="subtraction")

                    print("previous:",timestamp_previous_iteration,"current:",timestamp_current_iteration, "new:",new_timestamp)

                    head_output = f"{video_name.split('.')[0]}_mitte{counter-1}.mp4"
                    tail_output = f"{video_name.split('.')[0]}_tail{counter}.mp4"
                    print("PRINT: all Variables further cut:",input_file,new_timestamp,head_output,tail_output)

                    cut_in_2_pieces(input_file,new_timestamp,head_output,tail_output)
                    os.remove(input_file)

                    versions_to_concat[video_name].pop()
                    versions_to_concat[video_name].append(head_output)
                    versions_to_concat[video_name].append(f"{folder_path}{video_name.split('.')[0]}_pause{counter}.mp4")
                    versions_to_concat[video_name].append(tail_output)

                    counter += 1
        
            
except Exception as e:
    print("Error in insert_pause part:", e)


# In[ ]:


# Concat all the video snippets
try:
    for key, values in versions_to_concat.items():
        textfile_content = ""
        output = f"{key.split('.')[0]}_endprodukt.mp4"

        for value in values:
            dummy_string = f"file '{value}'\n"
            textfile_content = textfile_content + dummy_string

        # Create textfile with content
        textfile_name = "dummy.txt"
        with open(textfile_name, 'w') as textfile:
            textfile.write(textfile_content.rstrip())
            
        # Concat the videos
        print("key:",key,"ouput:",output,"textfile_content:", textfile_content)
        concatenate_videos(textfile_name, output)

except Exception as e:
    print(e)


# ## File Handling

# In[ ]:


# delete byproducts
try:
    for key, values in versions_to_concat.items():
        if os.path.exists(folder_path + key):
            os.remove(folder_path + key)

        for value in values:
            os.remove(value)
            
except Exception as e:
    print(e)


# In[ ]:


# Move endprodukte
for f in os.listdir():
    if f.endswith("endprodukt.mp4"):
        shutil.move(f,folder_path)


# In[ ]:


# Rename files
for f in os.listdir(folder_path):
    if f.endswith("endprodukt.mp4"):
        new_name = remove_end_in_name(f)
        new_name = new_name + ".mp4"
        os.rename(folder_path+f, folder_path+new_name)


# # Start cut_and_keep script

# In[ ]:


#loop through videonames and then through columns to divide
folder_path = "endprodukte/"

try:
    for row, video_name in video_schnitt_df["dateiname"].items():
        columns_to_divide = get_columns_to_divide(video_schnitt_df)
        for col_num,col in enumerate(video_schnitt_df[columns_to_divide]):

            # check wether teilen colum has a value
            if video_schnitt_df[col][row] != "nan":

                # Wenn mehr als eine Teilung
                if col_num > 0:
                    
                    # define input_file
                    input_file = f"{video_name.split('.')[0]}_tail{col_num}.mp4"

                    # define timestamp
                    timestamp_previous_iteration = calculate_timestamp(columns_to_divide[col_num -1], row)
                    timestamp_current_iteration = calculate_timestamp(col, row)
                    new_timestamp = calculate_time(timestamp_current_iteration, timestamp_previous_iteration, kind="subtraction")

                    print("previous:",timestamp_previous_iteration,"current:",timestamp_current_iteration, "new:",new_timestamp)
                    
                    # define output
                    head_output = f"{video_name.split('.')[0]}_mitte{col_num+ 1}.mp4"
                    tail_output = f"{video_name.split('.')[0]}_tail{col_num +1}.mp4"
                    
                    print("PRINT: all Variables further cut:",input_file,new_timestamp,head_output,tail_output)

                    cut_in_2_pieces(input_file,new_timestamp,head_output,tail_output)
                    os.remove(input_file)
                
                # Start bei mindestens einer Teilung
                else:

                    # define input_file
                    if video_schnitt_df["standbild_bis"][row] == "nan" and video_schnitt_df["rausschneiden1_bis"][row] == "nan" and video_schnitt_df["pause1_bei"][row] == "nan":
                        input_file = video_name
                        
                    else:
                        input_file = folder_path + video_name
                    
                    # define timestamp                
                    new_timestamp = calculate_timestamp(col,row)
                    
                    head_output = f"{video_name.split('.')[0]}_head{col_num +1}.mp4"
                    tail_output = f"{video_name.split('.')[0]}_tail{col_num +1}.mp4"
                    
                    print("all variables:",input_file,new_timestamp,head_output,tail_output)

                    #start separation
                    cut_in_2_pieces(input_file,new_timestamp,head_output,tail_output)
except Exception as e:
    print("Error in cut and keep script:", e)


# # Create folder, move and delete files

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


# In[ ]:


folder_path = "endprodukte/"


for row, video_name in video_schnitt_df["dateiname"].items():
    original_prefix = video_name.split('.')[0]
    pattern = re.compile(rf'^{re.escape(original_prefix)}_(head\d+|mitte\d+|tail\d+).*$')
    
    try:    
        for f in os.listdir(folder_path):
            if pattern.match(f):
                print("video_name",video_name,"original_prefix:", original_prefix,"file",f)
                os.remove(folder_path + video_name)
    except Exception as e:
        print(e, "or this file already has been removed")


# In[ ]:


os.remove("dummy.txt")


# In[ ]:


print("Script reached its end")

