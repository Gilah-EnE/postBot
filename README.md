# postBot
 An automated post bot for Telegram that sends pictures from a folder with fixed intervals or according to the timetable. Useful for channels with artwork or pictures, especially if admins are lazy :)
## Usage
 - Install requirements from file ``` pip install -r requirements.txt ```
 - Edit configuration file (config.py is deprecated)
 - Run main.py
## Config parameters
### main
| Parameter | Description |
|---|--------------------------|
| api_id 	| Get on my.telegram.org 	|
| api_hash 	| Get on my.telegram.org 	|
| channel_link 	| Link to channel, only public channels are supported, "me" to send to saved messages 	|
### proxy
| Parameter | Description |
|---|--------------------------|
|use  	|(true/false), use proxy or not.  	|
|scheme  	|(SOCKS4/SOCKS5/HTTP), type of proxy  	|
|hostname  	|URL of proxy server  	|
|port  	|Port number  	|
|username  	|Username (can be empty)  	|
|password  	|Password (can be empty)  	|
### setup
| Parameter | Description |
|---|--------------------------|
|mode  	|(fixed_interval/manual), selects generation mode. Fixed interval means that you enter start and final hour values and intervals. The fixed mode works with pre-defined slots. 	|
|start_hour  	|When to land the first post.  	|
|stop_hour  	|When to land the last post.  	|
|interval  	|("hh:mm"), interval between posts  	|
|date_input_needed  	|(true/false), if unchecked, sends to current date.  	|
|verbose  	|(true/false), sends more output to console. 	|
|days_in_advance  	|How many days to fill in advance? 0 to disable.  	|
|use_caption  	|(true/false), activate to use caption under photo.  	|
### timetable
| Parameter | Description |
|---|--------------------------|
|manual_slots  	|(list), list of pre-defined slots. Works if the mode is "manual" 	|
### files
| Parameter | Description |
|---|--------------------------|
|path  	|Path to the folder with photos 	|
|accepted_formats  	|(list), file extensions that can be accepted 	|
|file_action  	|("remove"/"move"/"keep"), what to do with sent file ("remove" deletes it, "move" moves to new folder, "keep" does absolutely nothing) 	|
|caption_file  	|File with caption 	|
|temp_filename  	|Name for temp file with all sent posts 	|
|remove_temp_file  	|(true/false), keep or remove temp file, useful for debugging 	|
