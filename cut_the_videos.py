# %% [markdown]
# # Pseudo Code first

# %%
# load file into python (check data type. CSV or exel?)
# convert data into dataframe, with pandas
# clean and prepare data if must
# put the data into lists or dics 
# cut the videos with ffmpeg and/or subprocess(check wether its downloaded correctly)
#   cut the video on spcified time into two pieces

# %%
import pandas as pd
import subprocess

# %% [markdown]
# # Get the file and clean it

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
        '-c', 'copy',
        output_file
    ]
    
     # Run the command
    subprocess.run(command, check=True)

# %%
def get_video_duration(file_path):
    command = ['ffmpeg', '-i', file_path]
    result = subprocess.run(command, text=True, capture_output=True)
    output_lines = result.stderr.split('\n')
    duration_line = [line for line in output_lines if 'Duration' in line][0]
    duration = duration_line.strip().split(",")[0].split(" ")[1]
    return duration


# %%
video_schnitt_df = get_the_table_data()
video_schnitt_df = clean_the_data(video_schnitt_df)

# %% [markdown]
# # Cut head and tail

# %%
# videos need to be in same directory with python script
for idx, video_name in video_schnitt_df["dateiname"].items():
    output_file = f"{video_name}_ohne_start_ende.mp4"
    cut_head = video_schnitt_df["vorne_abschneiden_bis"][idx]
    cut_tail = video_schnitt_df["hinten_abschneiden_ab"][idx]

    cut_head_tail(video_name, output_file, cut_head, cut_tail)