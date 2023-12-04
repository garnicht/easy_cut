# %%
import pandas as pd
import subprocess
import os
import shutil

# %%
def get_video_duration(file_path):
    command = ['ffmpeg', '-i', file_path]
    result = subprocess.run(command, text=True, capture_output=True)
    output_lines = result.stderr.split('\n')
    duration_line = [line for line in output_lines if 'Duration' in line][0]
    duration = duration_line.strip().split(",")[0].split(" ")[1]
    return duration

# %%
def create_folder(folder_name):
    try:
        # Create a new folder in the current working directory
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")

# %%
def get_the_table_data():
    while True:
        table_path = input("What is the table path + name? (.../filename.csv):")
        try:
            video_schnitt_df = pd.read_csv(table_path)
            print("Table loaded succesfully")
            return video_schnitt_df
        except Exception as error:
            print("An error occured:", error)
            continue
        break

# %%
def clean_the_data(df):
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.strip()
    df = df.astype(str)
    print("Table Columns cleaned")
    return df

# %%
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

# %%
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

# %% [markdown]
# # Get the file and clean it

# %%
video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)

# %% [markdown]
# # remove more slices in a video

# %%
try:
    # videos need to be in same directory with python script
    for idx, video_name in video_schnitt_df["dateiname"].items():
        
        columns_to_cut = ["vorne_abschneiden_bis","rausschneiden_ab","rausschneiden_bis","cut2_ab","cut2_bis","cut3_ab","cut3_bis","cut4_ab","cut4_bis","cut5_ab","cut5_bis"]

        parts_list = []
        video1 = 0
        video2 = 0

        try:
            for i,col in enumerate(columns_to_cut):
                cut_head = video_schnitt_df[col][idx]
                cut_tail = video_schnitt_df[columns_to_cut[i+1]][idx]

                # logic to handle the nans
                if cut_head == "nan" and cut_tail == "nan":
                    break
                elif cut_head == "nan":
                    cut_head = "00:00:00"
                elif cut_tail == "nan":
                    cut_tail = get_video_duration(video_name)

                output_file = f"{video_name.split('.')[0]}_part{i}.mp4"
                
                cut_head_tail(video_name, output_file, cut_head, cut_tail)

                if i not in [1, 3, 5, 7, 9]:
                    parts_list.append(output_file)

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

        except:
            print("skip to next video")

except Exception as error:
    print("An error occured:", error)   

# %%
path_script_output = "script_output"
create_folder(path_script_output)

path_folder_parts = "script_output/parts"
create_folder(path_folder_parts)

# %%
original_video_names = list()

for video_name in video_schnitt_df["dateiname"]:
    if video_name != "nan":
        original_video_names.append(video_name)

# %%
for filename in os.listdir():
    if filename.endswith(".mp4") and filename not in original_video_names:
        shutil.move(filename,path_script_output)

# %%
for filename in os.listdir(path_script_output):
    if filename.find("concatted"):
        src = f"script_output/{filename}"
        shutil.move(src,path_folder_parts)


