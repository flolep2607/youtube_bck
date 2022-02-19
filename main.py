import requests
import json

# Get secret keys from JSON file
with open('keys.json') as json_file:
    key = json.load(json_file)

def save():
    with open('keys.json',"w") as json_file:
        json_file.write(json.dumps(key, indent=4))

subscribe_url = 'https://pubsubhubbub.appspot.com/subscribe'
data = {
    'hub.callback':key.get("callback_url"),
    'hub.verify': 'sync',#'async',
    'hub.mode': 'subscribe',
    'hub.lease_seconds': '828000'
}

while key.get("channels_todo").get("channel_id"):
    CHANNEL_ID=key.get("channels_todo").get("channel_id").pop(0)
    if CHANNEL_ID in key.get("channels_done").get("channel_id"):
        continue
    topic_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s'%CHANNEL_ID
    data['hub.topic']=topic_url
    print(topic_url,data.get('hub.callback'))
    response = requests.post(subscribe_url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
    print(CHANNEL_ID,response.status_code,response.text)
    if response.status_code==204:
        key.get("channels_done").get("channel_id").append(CHANNEL_ID)
        save()


while key.get("channels_todo").get("username"):
    USERNAME=key.get("channels_todo").get("username").pop(0)
    if USERNAME in key.get("channels_done").get("username"):
        continue
    topic_url = 'https://www.youtube.com/feeds/videos.xml?user=%s'%USERNAME
    data['hub.topic']=topic_url
    response = requests.post(subscribe_url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
    print(USERNAME,response.status_code,response.text)
    if response.status_code==204:
        key.get("channels_done").get("username").append(USERNAME)
        save()
save()