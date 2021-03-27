import glob
import subprocess
import datetime

#delete old output file
subprocess.run("rm output.mkv", shell=True)

#Download clips from Reddit
subprocess.run('youtube-dl $(curl -s -H "User-agent: \'your bot 0.1\'" https://www.reddit.com/r/IdiotsInCars/hot.json?limit=20 | jq \'.\' | grep url_overridden_by_dest | grep -Eoh "https:\/\/v\.redd\.it\/\w{13}")', shell=True)

#Check clips for kids or YT gets mad
kidCheck = input("Are the clips free of kids? (y/N): ")
if kidCheck == "y":
	pass
else:
	quit()

video_files = glob.glob("*.mp4")

#add silent audio track to videos with no audio
#https://stackoverflow.com/questions/12368151/adding-silent-audio-in-ffmpeg#12375018
audio_command = "ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i "
audio_command_back = " -c:v copy -c:a aac -shortest "

index = 0
for f in video_files:
	subprocess.run(audio_command + f + audio_command_back + "audio/" + str(index) + ".mp4", shell=True)
	index += 1

video_files = glob.glob("audio/*.mp4")

#convert all videos to the same sar and resolution
#https://unix.stackexchange.com/questions/190431/convert-a-video-to-a-fixed-screen-size-by-cropping-and-resizing
index = 0
for f in video_files:
	subprocess.run('ffmpeg  -i ' + f + ' -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1" -c:v mpeg4 -q:v 4 -c:a libmp3lame -q:a 4 fixed/' + str(index)  + ".mp4", shell=True)
	index += 1

video_files = glob.glob("fixed/*.mp4")

#Combine all clips into one video
#https://stackoverflow.com/questions/7333232/how-to-concatenate-two-mp4-files-using-ffmpeg#11175851
command = "ffmpeg"

for f in video_files:
	command += " -i " + f

command += ' -filter_complex "'

for f in range(0, len(video_files)):
	command += '[' + str(f) + ':v] [' + str(f) + ':a] '

command += 'concat=n=' + str(len(video_files)) + ':v=1:a=1 [v] [a]" -map "[v]" -map "[a]" output.mkv'
#print(command)
subprocess.run(command, shell=True)

#Upload video
#https://github.com/tokland/youtube-upload
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
epNum = '47'
subprocess.run('youtube-upload --title="Best Of Idiots In Cars ' + epNum + '" --description="The best videos of Idiots In Cars from ' + now + '. Like, comment, and subscribe! New video every day!\nWe take the best clips of idiots in cars, and combine them into the ultimate idiots in cars compilation! Witness epic car crashes, police cars in action, and some of the top car driving fails from Reddit." --category="Autos & Vehicles" --tags="idiots in cars, best of idiots in cars, idiots in cars highlights, idiots in cars top, idiots in cars reddit, idiots in cars compilation, total idiots driving in russia, idiots in cars police, idiots in cars clips, idiots in cars driving fails, epic car fails, idiots in car, idiot in car, epic car crashes, dash cam footage, totoal idiots on the road, car crash compilation, epic dash cam video, best of idiots in cars ' + epNum + '" --default-language="en" --default-audio-language="en" --client-secrets="client_secrets.json" --credentials-file="my_credentials.json" output.mkv', shell=True)

#Delete un-needed files
subprocess.run("rm fixed/*.mp4", shell=True)
subprocess.run("rm audio/*.mp4", shell=True)
subprocess.run("rm *.mp4", shell=True)
