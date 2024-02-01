# What is this repo for? 

The goal is to reduce the amount of time my stakeholder needs to manually cut his videos. This is why he asked me to write a script that needs to do the following: 
- read a list full of names and timestamps 
- execute different cut-commands with the help of ffmpeg 
- store the end product, side products and original videos at the right place

# Next steps
- [x] testing the existing loops
- [x] create concat function to concat the merged video with cutted_original
- [x] write for loop to get through the list and concatenate all the existing videos
- [x] create a loop to remove and concat videos
- [x] create a cut into pieces function
- [x] edit the cut_the_videos so all endprodukte move to the right folderand maybe are renamed
- [x] improve all the .py files to also accept the last cut timestamp. Right now there still needs some manuel manipulation to be done
- [x] csv soll kein input sein, take csv in directory
- [x] bug: part10 was not created, script ended at part9, end is missing some minutes or seconds
- [x] spaltennamen ändern und im Script anpassen cut_things_out
- [x] Script anpassen, sodass unendlich viel gecutted werden kann.
- [x] bug: If one video_name consists exact part of another video_name, renaming does not work properly (need to change startswith prefix)
- [x] spaltennamen ändern und im Script anpassen durch_standbild_ersetzen
- [x] spaltennamen ändern und im Script anpassen cut_and_keep + small copy test
- [x] combine script one and two
- [x] solve the special case
- [x] test this script
- [ ] edit combined script so renaming also doesnt fail there (also think about part6 error, where the youngest vid is also a part one)
- [ ] add last script 
- [ ] alle scripte testen
- [ ] restructure ur scripts to one exe
- [ ] delete the nebenprodukte
- [ ] improve performance with ignoring the cut of odd parts 
- [ ] bug: when script standbild_ersetzen is runned, all original_videos not in csv (was an special csv) also got removed into script_output folder
- [ ] rename the endprodukte to original video_name
- [ ] adding pauses into video
- [ ] change the rename system of cut_things_out to also use regular expression (higher consistency)
- [ ] performance update -> switch part1 from cut_things_out with merged_start from standbild_ersetzen
- [ ] performance update -> looks like It may be possible to just copy in durch_standbild_ersetzen
- [ ] delete dummy.txt in the end

# What are the different executions / files? 
- cut_and_keep -> this script allows to cut the videos at given timestamp and saves both outputs 
- cut_things_videos -> this script allows to cut at two specified points during the video. In the end som parts should be kept and concatted together and some parts should be deleted
- durch_standbild_ersetzen -> this file gives my stakeholder the opportunity to replace a specified range in the video with a given image and keeps the audio. 
- cut_the_videos -> was the first trial to combine all of the scripts above. Fatally failed :D needs to be adjusted and thought through again.  
