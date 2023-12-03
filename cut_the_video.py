# %%
import pandas as pd
import subprocess

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
def get_video_duration(file_path):
    command = ['ffmpeg', '-i', file_path]
    result = subprocess.run(command, text=True, capture_output=True)
    output_lines = result.stderr.split('\n')
    duration_line = [line for line in output_lines if 'Duration' in line][0]
    duration = duration_line.strip().split(",")[0].split(" ")[1]
    return duration

# %%
def get_tail(input_file,output_file,timestamp):

    # -ss = ab dort; -to = bis dort
    command = ['ffmpeg', '-i', input_file, '-ss', timestamp, '-c', 'copy', output_file]

    # Execute the commands
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# %%
def get_head(input_file,output_file,timestamp):

    # -ss = output ab dort; -to = output bis dort 
    command = ['ffmpeg', '-i', input_file, '-to', timestamp, '-c', 'copy', output_file]

    # Execute the commands
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# %%
def cut_in_2_pieces(input_file, timestamp, head_output, tail_output):
    
    # -ss = ab dort; -to = bis dort
    head_cmd = ['ffmpeg', '-i', input_file, '-to', timestamp, '-c', 'copy', head_output]
    tail_cmd = ['ffmpeg', '-i', input_file, '-ss', timestamp, '-c', 'copy', tail_output]

# Execute the commands
    try:
        subprocess.run(head_cmd, check=True)
        subprocess.run(tail_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# %%
def cut_between_pieces(input_file,output_file,cut_head,cut_tail):

    # -ss = ab dort; -to = bis dort
    command = ['ffmpeg', '-i', input_file, '-to', cut_head, '-c', 'copy', head_output]
    command = ['ffmpeg', '-i', input_file, '-to', cut_tail, '-c', 'copy', tail_output]
    
    try:
        subprocess.run(command,check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# %%
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
        '-c:v', 'copy', output_file
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# %%
def merge_audio_and_video(video_file,audio_file,output_file):
    #Construct command
    command = ['ffmpeg',
               '-i', video_file,
               '-i', audio_file,
               '-c:v', 'copy',
               '-c:a', 'aac', output_file
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

# %%
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

# %% [markdown]
# # Get the file and clean it

# %%
video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)

# %% [markdown]
# # Cut head and tail

# %%
# videos need to be in same directory with python script
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        output_file = f"{video_name.split(".")[0]}_ohne_start_ende.mp4"
        cut_head = video_schnitt_df["vorne_abschneiden_bis"][idx]
        cut_tail = video_schnitt_df["hinten_abschneiden_ab"][idx]

        #building logic when just to cut head or tail
        if str(cut_head) == "nan" and str(cut_tail) == "nan":
            continue
        if str(cut_head) == "nan":
            cut_head = "00:00:00"
        if str(cut_tail) == "nan":
            cut_tail = "01:30:00"
    
        print(video_name,cut_head, cut_tail)
        cut_head_tail(video_name, output_file, cut_head, cut_tail)
except Exception as error:
    print("An error occurred:", error)

# %% [markdown]
# # Get Standbild

# %%
# videos need to be in same directory with python script
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        output_file = f"{video_name.split(".")[0]}_standbild.mp4"
        cut_head = video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]

        #building logic when just to cut head or tail
        if str(cut_head) == "nan":
            continue
        
        get_standbild(video_name,output_file,cut_head)
except Exception as error:
    print("An error occurred:", error)

# %% [markdown]
# # Get audio

# %%
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():
        
        if str(video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]) == "nan":
            continue
        # timedelta = cut_tail - pd.to_timedelta(cut_head)
        # dummy_date = pd.Timestamp('1900-01-01')
        # new_timestamp = dummy_date + timedelta
        # cut_tail = new_timestamp.strftime('%H:%M:%S.%f')[:-3]

        #Define arguments
        output_file = f"{video_name.split(".")[0]}_head_audio.mp4"
        cut_head = video_schnitt_df["vorne_abschneiden_bis"][idx]
        cut_tail = video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]

        if str(cut_head) == "nan":
            cut_head = "00:00:00"

        print("video_name",video_name,"output_file", output_file,"cut_head",cut_head,"cut_tail:", cut_tail)
        get_audio(video_name,output_file,cut_head,cut_tail)

except Exception as error:
    print("An error occurred:", error)

# %% [markdown]
# # Merge audio and video

# %%
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        if str(video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]) == "nan":
            continue
        video_file = f"{video_name.split(".")[0]}_standbild.mp4"
        audio_file = f"{video_name.split(".")[0]}_head_audio.mp4"
        output_file = f"{video_name.split(".")[0]}_merged_start.mp4"
        
        merge_audio_and_video(video_file,audio_file,output_file)

except Exception as error:
    print("An error occured:", error)

# %% [markdown]
# # Concatenate videos to end product

# %%
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        #define input for the text file with the videos we want to concat
        video1 = f"{video_name.split(".")[0]}_merged_start.mp4"
        video2 = video_name
        textfile_content = f"file '{video1}'\nfile '{video2}'"

        #create the file with content
        with open('dummy.txt', 'w') as textfile:
            textfile.write(textfile_content)

        #define parameters for concat function
        output_file = f"{video_name.split(".")[0]}_endprodukt_trimmed.mp4"
        textfile_name = "dummy.txt"

        concatenate_videos(textfile_name,output_file)
        
except Exception as error:
    print("An error occured:", error)

# %% [markdown]
# # Remove and Concat

# %%
#Get Head
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        #Logik da nicht alle Videos vorher beschnitten sein müssen
        if all(str(video_schnitt_df[col][idx]) == "nan" for col in ["vorne_abschneiden_bis", "hinten_abschneiden_ab", "vorne_bild_durch_standbild_ersetzen_bis"]):
            input_file = video_name
        elif str(video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]) == "nan":
            input_file = f"{video_name.split(".")[0]}_ohne_start_ende.mp4"
        else:
            input_file = f"{video_name.split(".")[0]}_endprodukt_trimmed.mp4"

        timestamp = str(video_schnitt_df["rausschneiden_ab"][idx])
        output_file = f"{video_name.split(".")[0]}_head.mp4"

        get_head(input_file,output_file,timestamp)
        
        continue
except Exception as error:
    print("An error occured:", error)   

# %%
#Get Tail
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        #Logik da nicht alle Videos vorher beschnitten sein müssen
        if all(str(video_schnitt_df[col][idx]) == "nan" for col in ["vorne_abschneiden_bis", "hinten_abschneiden_ab", "vorne_bild_durch_standbild_ersetzen_bis"]):
            input_file = video_name
        elif str(video_schnitt_df["vorne_bild_durch_standbild_ersetzen_bis"][idx]) == "nan":
            input_file = f"{video_name.split(".")[0]}_ohne_start_ende.mp4"
        else:
            input_file = f"{video_name.split(".")[0]}_endprodukt_trimmed.mp4"

        timestamp = video_schnitt_df["rausschneiden_bis"][idx]
        output_file = f"{video_name.split(".")[0]}_tail.mp4"

        get_tail(input_file,output_file,timestamp)
        
        continue
except Exception as error:
    print("An error occured:", error)   

# %%
# Concat head and tail
try:
    for idx, video_name in video_schnitt_df["dateiname"].items():

        #define input for the text file with the videos we want to concat
        video1 = f"{video_name.split(".")[0]}_head.mp4"
        video2 = f"{video_name.split(".")[0]}_tail.mp4"
        textfile_content = f"file '{video1}'\nfile '{video2}'"

        #create the file with content
        with open('dummy.txt', 'w') as textfile:
            textfile.write(textfile_content)

        #define parameters for concat function
        output_file = f"{video_name.split(".")[0]}_endprodukt_remove_and_concat.mp4"
        textfile_name = "dummy.txt"

        concatenate_videos(textfile_name,output_file)
        
except Exception as error:
    print("An error occured:", error)
