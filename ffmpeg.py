import glob
import subprocess
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw 

def downloadClips():
	headers = {
		'User-Agent': 'car bot'
	}
	page = requests.get('https://www.reddit.com/r/IdiotsInCars/hot.json?limit=50', headers = headers)
	reddit = page.json()

	command = 'youtube-dl '
	for url in reddit['data']['children']:
		tmp = url['data']['url_overridden_by_dest']
		if 'v.redd.it' in tmp:
			command += tmp + " "
		elif 'streamable' in tmp:
			command += tmp + " "
		elif 'youtu.be' in tmp:
			command += tmp + " "

	subprocess.run(command, shell=True)

def main():
	#delete old output files
	subprocess.run("rm output.mkv", shell=True)
	subprocess.run("rm thumbnail.jpg", shell=True)

	#Download clips from Reddit
	downloadClips()

	#Check clips for kids or YT gets mad
	#kidCheck = input("Are the clips free of kids? (y/N): ")
	#if kidCheck == "y":
	#	pass
	#else:
	#	quit()

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

	#Get episode number
	now = datetime.now()
	og_date = datetime.strptime('2021-03-04', "%Y-%m-%d")
	str_now = now.strftime("%Y-%m-%d")
	epNum = str((now - og_date).days)

	#Create screen shot
	video_input_path = 'output.mkv'
	img_output_path = 'thumbnail.jpg'
	subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:05.000', '-vframes', '1', img_output_path])

	x, y = 50, 15
	fillcolor = "white"
	shadowcolor = "black"
	text = "Idiots In Cars " + epNum
	emoji = ['💥', '🔥', '😂', '😱', '🤣', '🤯', '👌', '🤬', '🤡', '🚔', '🚘']

	thumbnail = Image.open("thumbnail.jpg")
	font = ImageFont.truetype('fonts/Anton-Regular.ttf', 200)
	image_edit = ImageDraw.Draw(thumbnail)

	#https://stackoverflow.com/questions/41556771/is-there-a-way-to-outline-text-with-a-dark-line-in-pil
	image_edit.text((x-5, y-5), text, font = font, fill = shadowcolor)
	image_edit.text((x+5, y-5), text, font = font, fill = shadowcolor)
	image_edit.text((x-5, y+5), text, font = font, fill = shadowcolor)
	image_edit.text((x+5, y+5), text, font = font, fill = shadowcolor)

	image_edit.text((x, y), text, font = font, fill = fillcolor)
	thumbnail.save("thumbnail.jpg")

	#Upload video
	#https://github.com/tokland/youtube-upload

	subprocess.run('youtube-upload --title="Best Of Idiots In Cars ' + epNum + '" --description="The best videos of Idiots In Cars from ' + str_now + '. Like, comment, and subscribe! New video every day!\nWe take the best clips of idiots in cars, and combine them into the ultimate idiots in cars compilation! Witness epic car crashes, police cars in action, the best dash cam footage, and some of the top car driving fails on the internet." --category="Autos & Vehicles" --tags="idiots in cars, best of idiots in cars, idiots in cars highlights, dashcam fails, idiots in cars reddit, dash cam accidents, total idiots driving in russia, idiots in cars police, idiots in cars clips, idiots in cars driving fails, epic car fails, idiots in car, car crash compilation, epic car crashes, dash cam footage, totoal idiots on the road, car crash compilation, epic dash cam video, road rage, best of idiots in cars ' + epNum + '" --thumbnail="thumbnail.jpg" --default-language="en" --default-audio-language="en" --client-secrets="client_secrets.json" --credentials-file="my_credentials.json" output.mkv', shell=True)

	#Delete un-needed files
	subprocess.run("rm fixed/*.mp4", shell=True)
	subprocess.run("rm audio/*.mp4", shell=True)
	subprocess.run("rm *.mp4", shell=True)

if __name__ == "__main__":
	main()
