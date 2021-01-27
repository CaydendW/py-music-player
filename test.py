# import json
# class playlistcontroll:
#    def newsong(url, title, channel, duration, views):
#       return {"url": url, "title": title, "channel": channel, "duration": duration, "views": views}

#    def newplaylist(name):
#       return {"name": name, "songs": []}

#    def newplaycollection():
#       return {"playlists": []}

# def doserialize(inp):
#    return json.dumps(inp, indent=3)

# def dodeserialize(inp):
#    return json.loads(inp)

# song1 = playlistcontroll.newsong("a", "b", "c", "d", "e")

# playlist1 = playlistcontroll.newplaylist("PLACEHOLD")

# whole = playlistcontroll.newplaycollection()
# whole['playlists'].append(playlist1)
# whole['playlists'][0]['songs'].append(song1)