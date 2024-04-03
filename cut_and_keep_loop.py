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
                    continue
                    # define input_file
                    input_file = f"{video_name.split('.')[0]}_tail{col_num}.mp4"

                    # define timestamp. This time we also need to subtract duration of head_output because we use tail_output
                    timestamp_original = video_schnitt_df[col][row]
                    if not timestamp_head_output:
                      timestamp_head_output = new_timestamp
                    else timestamp_head_output
                  
                      # get diff from cutted videos and subtract
                    diff_with_cuts = calculate_timestamp(timestamp_original, row, kind="diff_with_cuts")
                    new_timestamp_tail = calculate_time(timestamp_original, diff_with_cuts, kind="subtraction")

                      # get diff from pauses and add
                    diff_with_pauses = calculate_timestamp(timestamp_original, row, kind="diff_with_pauses")
                    new_timestamp_tail = calculate_time(new_timestamp_tail, diff_with_pauses, kind="addition")

                      # subtract timestamp_head_output from original_timestamp
                    new_timestamp_tail = calculate_time(new_timestamp_tail, timestamp_head_output, kind="subtraction")
                    
                    timestamp_head_output = new_timestamp_tail
              
                    # define outputs
                    head_output = f"{video_name.split('.')[0]}_mitte{col_num+ 1}.mp4"
                    tail_output = f"{video_name.split('.')[0]}_tail{col_num +1}.mp4"
                  
                    print("PRINT: all Variables further cut:",input_file,timestamp,head_output,tail_output)

                    #cut_in_2_pieces(input_file,new_timestamp_tail,head_output,tail_output)
                    #os.remove(input_file)
                
                # Start bei mindestens einer Teilung
                else:

                    # define input_file
                    if video_schnitt_df["standbild_bis"][row] == "nan" and video_schnitt_df["rausschneiden1_bis"][row] == "nan" and video_schnitt_df["pause1_bei"][row] == "nan":
                        input_file = video_name
                        
                    else:
                        input_file = folder_path + video_name
                    
                    # define timestamp                
                    timestamp_original = video_schnitt_df[col][row]

                    # get diff from cutted videos and subtract
                    diff_with_cuts = calculate_timestamp(timestamp_original, row, kind="diff_with_cuts")
                    new_timestamp = calculate_time(timestamp_original, diff_with_cuts, kind="subtraction")

                    # get diff from pauses and add
                    diff_with_pauses = calculate_timestamp(timestamp_original, row, kind="diff_with_pauses")
                    new_timestamp = calculate_time(new_timestamp, diff_with_pauses, kind="addition")
                    
                    head_output = f"{video_name.split('.')[0]}_head{col_num +1}.mp4"
                    tail_output = f"{video_name.split('.')[0]}_tail{col_num +1}.mp4"
                    
                    print("all variables:",input_file,new_timestamp,head_output,tail_output)

                    #start separation
                    #cut_in_2_pieces(input_file,new_timestamp,head_output,tail_output)
except Exception as e:
    print("Error in cut and keep script:", e)
