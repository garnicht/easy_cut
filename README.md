# What is this repo for? 
The goal is to reduce the amount of time my stakeholder needs to manually cut his videos. This is why he asked me to write a script that needs to do the following: 
- read a list full of videonames and timestamps 
- execute different cut-commands with the help of ffmpeg 
- store the end products, side products and original videos at the right place

# Next possible steps
- [ ] QOL -> remove bug that causes the need of 3 free columns in cut things out. 
- [ ] in general improve the older cut things out logic with newer code logic
- [ ] QOL -> rename endprodukt nach cut and keep from head, mitte(1-X) and tail to -> part1-X
- [ ] performance update -> ignore the cut of odd parts in cut_things_out
- [ ] performance update -> switch part1 from cut_things_out with merged_start from standbild_ersetzen
- [ ] performance update -> looks like It may be possible to just copy in durch_standbild_ersetzen

# How to use the combined_all.py file?
- Combined_all.py has to be in same directory as video files and the .csv with the timestamps 
- The .csv need to have the columns and structure like the csv in the backup directory
- timestamps need to have following format: "hh:mm:ss" or "hh:mm:ss.msmsms"
- the columns "rausschneiden1_ab" etc. need to have 3 empty columns in the end
    - script woun't work without that preparation -> error code is gonna give information then
- no Umlaute like Ä Ü Ö in video names 
- all commands beside standbild ersetzen, are infinitely expandable when using given column structure
- when script is finished, all edited videos are found in new folder called "endprodukte"
- if a video needs to be divided into pieces, the endproducts are like this: video_name_head -> video_name_mitte(1-X) ... -> video_name_tail