import glob
import subprocess
import datetime

#Download clips from Reddit
subprocess.run('youtube-dl $(curl -s -H "User-agent: \'your bot 0.1\'" https://www.reddit.com/r/IdiotsInCars/hot.json?limit=20 | jq \'.\' | grep url_overridden_by_dest | grep -Eoh "https:\/\/v\.redd\.it\/\w{13}")', shell=True)

video_files = glob.glob("/home/zefrof/Documents/youtube/*.mp4")

#add silent audio track to videos with no audio
#https://stackoverflow.com/questions/12368151/adding-silent-audio-in-ffmpeg#12375018
audio_command = "ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i "
audio_command_back = " -c:v copy -c:a aac -shortest "

index = 0
for f in video_files:
	subprocess.run(audio_command + f + audio_command_back + "/home/zefrof/Documents/youtube/audio/" + str(index) + ".mp4", shell=True)
	index += 1

video_files = glob.glob("/home/zefrof/Documents/youtube/audio/*.mp4")

#convert all videos to the same sar and resolution
#https://unix.stackexchange.com/questions/190431/convert-a-video-to-a-fixed-screen-size-by-cropping-and-resizing
index = 0
for f in video_files:
	subprocess.run('ffmpeg  -i ' + f + ' -vf "scale=(iw*sar)*max(1920/(iw*sar)\,1080/ih):ih*max(1920/(iw*sar)\,1080/ih), crop=1920:1080,setsar=1:1" -c:v mpeg4 -vtag XVID -q:v 4 -c:a libmp3lame -q:a 4 /home/zefrof/Documents/youtube/fixed/'  + str(index)  + ".avi", shell=True)
	index += 1

video_files = glob.glob("/home/zefrof/Documents/youtube/fixed/*.avi")

#Combine all clips into one video
#https://stackoverflow.com/questions/7333232/how-to-concatenate-two-mp4-files-using-ffmpeg#11175851
command = "ffmpeg"

for f in video_files:
	command += " -i " + f

command += ' -filter_complex "'

for f in range(0, len(video_files)):
	command += '[' + str(f) + ':v] [' + str(f) + ':a] '

command += 'concat=n=' + str(len(video_files)) + ':v=1:a=1 [v] [a]" -map "[v]" -map "[a]" /home/zefrof/Documents/youtube/output.mkv'
subprocess.run(command, shell=True)

#Upload video
#https://github.com/tokland/youtube-upload
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
print('youtube-upload --title="Best Of Idiots In Cars ' + now + '" --description="The best videos of Idiots In Cars from ' + now + '" --category="Autos & Vehicles" --tags="idiots in cars, best of idiots in cars, idiots in cars highlights, idiots in cars top, idiots in cars reddit, idiots in cars compilation, idiots in cars reaction, idiots in cars police, idiots in cars clips, idiots in cars driving fails" --default-language="en" --default-audio-language="en" --client-secrets="/home/zefrof/Documents/youtube/client_secrets.json" --credentials-file="/home/zefrof/Documents/youtube/my_credentials.json" /home/zefrof/Documents/youtube/output.mkv')
#subprocess.run('youtube-upload --title="Best Of Idiots In Cars ' + now + '" --description="The best videos of Idiots In Cars from ' + now + '" --category="Autos & Vehicles" --tags="idiots in cars, best of idiots in cars, idiots in cars highlights, idiots in cars top, idiots in cars reddit, idiots in cars compilation, idiots in cars reaction, idiots in cars police, idiots in cars clips, idiots in cars driving fails" --default-language="en" --default-audio-language="en" --client-secrets="/home/zefrof/Documents/youtube/client_secrets.json" --credentials-file="/home/zefrof/Documents/youtube/my_credentials.json" /home/zefrof/Documents/youtube/output.mkv', shell=True)

#Delete un-needed files
subprocess.run("rm /home/zefrof/Documents/youtube/fixed/*.avi", shell=True)
subprocess.run("rm /home/zefrof/Documents/youtube/audio/*.mp4", shell=True)
subprocess.run("rm /home/zefrof/Documents/youtube/*.mp4", shell=True)
#subprocess.run("rm /home/zefrof/Documents/youtube/*.mkv", shell=True)
