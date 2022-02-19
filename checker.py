# coding: utf-8
import requests
import json
import queue
import dateutil.parser
import xmltodict
import pathlib
from yt_dlp import YoutubeDL


LAST={}
class FILE(object):
    def __init__(self, filename):
        self.filename = filename+'.json'
        with open(self.filename) as json_file:
            self.data = json.load(json_file)
    def save(self):
        with open(self.filename,"w") as json_file:
            json_file.write(json.dumps(self.data, indent=4))
    def get_last(self,key):
        return self.data.get(key)
    def is_last(self,key,value):
        return self.get_last(key)==value
    def get_last_time(self,channel_id):
        if self.data.get(channel_id):
            return self.data.get(channel_id).get("time")
        else:
            return 0
    def set_last(self,channel_id,value,time=0):
        if time and self.data.get(channel_id) and self.data[channel_id].get("time"):
            if self.data[channel_id].get("time")<time:
                self.data[channel_id]={'value':value,'time':time}
        else:
            self.data[channel_id]={'value':value,'time':time}
        self.save()

keys=FILE('keys')
LAST=FILE('last')

        
def ytdl_hook(d):
    if d['status'] == 'finished':
        print('Done downloading')
ydl_opts = {
    # 'format': 'best',
    'format':'bestvideo[height<=?1080]+bestaudio/best',
    # 'progress_hooks': [ytdl_hook],
    "outtmpl":"videos/%(channel_id)s/%(id)s/%(title)s.%(ext)s",
}
ydl=YoutubeDL(ydl_opts)
TODOWNLOAD_QUEUE=queue.Queue()

def download(video_id):
    retries=0
    while retries<5:
        try:
            ydl.download(['https://www.youtube.com/watch?v=%s'%video_id])
            break
        except Exception as e:
            print(e)
            retries+=1
            print("Retrying...")
            continue
    # !!!
    # LAST.set_last(CHANNEL_ID,video_id,time)
    
def get_new(CHANNEL_ID):
    print(CHANNEL_ID)
    rep=requests.get('https://www.youtube.com/feeds/videos.xml?channel_id=%s'%CHANNEL_ID)
    dom=xmltodict.parse(rep.content)
    last_time=LAST.get_last_time(CHANNEL_ID)
    for entry in dom["feed"]["entry"]:
        time=int(dateutil.parser.isoparse(entry.get('published')).timestamp())
        if time<=last_time:
            continue
        video_id=entry.get('yt:videoId')
        pathlib.Path('videos/%s/%s/'%(CHANNEL_ID,video_id)).mkdir(parents=True, exist_ok=True)
        open("videos/%s/%s/data.json"%(CHANNEL_ID,video_id),'w').write(json.dumps(entry, indent=4))
        download(video_id)
        LAST.set_last(CHANNEL_ID,video_id,time)
        # TODOWNLOAD_QUEUE.put((CHANNEL_ID,video_id,time))
        
        
    # LAST.is_last()

for CHANNEL_ID in [*keys.data.get("channels_todo").get("channel_id"),*keys.data.get("channels_done").get("channel_id")]:
    get_new(CHANNEL_ID)




