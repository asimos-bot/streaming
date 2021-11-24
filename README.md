# Streaming

## Install 

```
sudo apt install portaudio19-dev
pip3 install -r requirements.txt
```

## User Information

```
{
    "ID": "username",
    "account_type": "premium/guest"
}
```

## Streaming Service Actions

Streaming Sessions can have one or more members.

for guest users, they can watch any kind of video alone or with a group if they belong to it.

for premium users, they can do what guest users do and also create and manage groups. They control
the video stream of their group.

Keep sending stream to clients that asked for it, until they tell the server to stop.

* `LIST_VIDEOS` - Return list with the available videos.
* `STREAM_VIDEO` - If user is premium, starts sending streaming packets of this video to any client from the premium user
group that asks to watch it. Only the client that sent this can specify the video quality. This command creates a room
* `USER_INFORMATION` - Answer with user status, after checking them with the service manager. Shows what videos this user is
streaming.
* `STOP_STREAM` - Stops streaming this user's stream, if they where streaming one.
* `PLAY_STREAM_TO_GROUP` - Premium users can use this command to stream to all users of its group
