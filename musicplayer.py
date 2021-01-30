try:
   import os
   import json
   import fcntl
   import random
   import struct
   import termios
   import argparse
   import subprocess

   from json import decoder
   from youtube_search import YoutubeSearch
except ImportError as e:
   print("Not all dependencies have been installed! Exiting!")
   exit()

version = "0.0.1"

cmdinput = None
f = None
playlistarray = None
downloadarray = None
volume = None
results = None
clearbool = None
videobool = None

class playlistfuncs:
   def newsong(url, title, channel, duration, views):
      return {"url": url, "title": title, "channel": channel, "duration": duration, "views": views}

   def newplaylist(name):
      return {"name": name, "songs": []}

   def newplaycollection():
      return {"playlists": []}

   def playlistalreadyexists(name):
      for i in range(len(playlistarray['playlists'])):
         if (playlistarray['playlists'][i]['name'] == name):
            return True
         else:
            pass
      return False

   def listplaylists():
      for i in range(len(playlistarray['playlists'])):
         print(i + 1, end='')
         print(". ", end='')
         print(playlistarray['playlists'][i]['name'])

   def listsongs(index):
      tw = int(terminal_size()[0])
      formated = '. %-{a}s %-{b}s %-{c}s %-{d}s'.format(a=int(tw*0.54), b=int(tw*0.2), c=int(tw*0.13), d=int(tw*0.10))

      for i in range(len(playlistarray['playlists'][index]['songs'])):
         print(i + 1, end='')
         print(formated % (playlistarray['playlists'][index]['songs'][i]['title'], playlistarray['playlists'][index]['songs'][i]['channel'], playlistarray['playlists'][index]['songs'][i]['views'], playlistarray['playlists'][index]['songs'][i]['duration']))

class cheeckygoto(Exception):
   pass

def mainloop():
   global resarray
   global titlearray
   global durationarray
   global viewarray
   global channelarray
   global volume
   global results
   global videobool

   clear()

   while True:
      try:
         cmdinput = input("Music-cmd > ")
      except EOFError:
         doexit()

      clear()

      cmdinput = cmdinput.split(' ')
      cmd = cmdinput[0]

      try:
         if (cmd == 'h'):
            dohelp()

         elif (cmd == '?'):
            if (len(cmdinput) > 1):
               del cmdinput[0]
               tmpresarray = dosearchyt(' '.join(cmdinput), results)
               resarray = tmpresarray['urls']
               titlearray = tmpresarray['titles']
               channelarray = tmpresarray['channels']
               viewarray = tmpresarray['views']
               durationarray = tmpresarray['durations']

               doprintsearchinfo()
            else:
               inp = input("Input search term > ")

               if (inp != ""):
                  tmpresarray = dosearchyt(inp, results)
                  
                  resarray = tmpresarray['urls']
                  titlearray = tmpresarray['titles']
                  channelarray = tmpresarray['channels']
                  viewarray = tmpresarray['views']
                  durationarray = tmpresarray['durations']

                  doprintsearchinfo()
               else:
                  print("Nothing searched!")
         
         elif (cmd == '/'):
            if (len(cmdinput) > 1):
               del cmdinput[0]
               tmpresarray = dosearchyt(' '.join(cmdinput), results)
               resarray = tmpresarray['urls']
               titlearray = tmpresarray['titles']
               channelarray = tmpresarray['channels']
               viewarray = tmpresarray['views']
               durationarray = tmpresarray['durations']

               doprintsearchinfo()
            else:
               inp = input("Input search term > ")
               
               if (inp != ""):
                  tmpresarray = dosearchyt(inp, results)
                  
                  resarray = tmpresarray['urls']
                  titlearray = tmpresarray['titles']
                  channelarray = tmpresarray['channels']
                  viewarray = tmpresarray['views']
                  durationarray = tmpresarray['durations']

                  doprintsearchinfo()
               else:
                  print("Nothing searched!")

         elif (cmd == 'p'):
            if (dotestmusic): dostopmusic()

            try:
               doplay(resarray[int(cmdinput[1]) - 1])
            except IndexError:
               try:
                  inp1 = input("Input video number > ")
                  inp = resarray[int(inp1) - 1]

                  doplay(inp)
               except IndexError:
                  print("No such video!")
            except ValueError:
               print("Invalid number!")
            except NameError:
               print("You have not searched anything yet!")

         elif (cmd == 'i'):
            doprintsearchinfo()
         
         elif (cmd == 's'):
            dostopmusic()

         elif (cmd == 'v'):
            if (int(cmdinput[1]) > 100 or int(cmdinput[1]) < 0):
               print("Invalid input. Number too big/small")
            else:
               volume = int(cmdinput[1])
         
         elif (cmd == 'r'):
            if (0 >= int(cmdinput[1])):
               print("Number too small")
            else:
               results = int(cmdinput[1])
         
         elif (cmd == 'q'):
            doexit()

         elif (cmd == 'npl'):
            try:
               if (len(cmdinput) > 1):
                  del cmdinput[0]
                  name = ' '.join(cmdinput)
               else:
                  name = input("Input name > ")
                  if (name == ""):
                     raise cheeckygoto("Don't mind me")

               if (playlistfuncs.playlistalreadyexists(name)):
                  print("Playlist already exists")
               else:
                  playlistarray['playlists'].append(playlistfuncs.newplaylist(name=name))
            except cheeckygoto:
               print("Invalid name!")

         elif (cmd == 'pls'):
            global index

            try:
               playlistfuncs.listplaylists()
               plname = input("Input playlist name > ")

               doprintsearchinfo()
               songname = input("Input song number > ")

               try:
                  songname = int(songname)
                  if (songname > len(titlearray) + 1):
                     raise cheeckygoto("Goto")
               except ValueError:
                  raise cheeckygoto("Sneaky goto here")

               songname = songname - 1
               song = playlistfuncs.newsong(resarray[songname], titlearray[songname], channelarray[songname], durationarray[songname], viewarray[songname])
               index = -1
               
               for i in range(len(playlistarray['playlists'])):
                  if (playlistarray['playlists'][i]['name'] == plname):
                     index = i
                     break

               if (index == -1):
                  print("Playlist not found!")
               else:
                  playlistarray['playlists'][index]['songs'].append(song)

            except cheeckygoto:
               print("Not a valid song number!")

         elif (cmd == 'dls'):
            index = -1

            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) - 1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  playlistfuncs.listsongs(index)

                  try:
                     songname = int(input("Input song number > "))
                     if (songname - 1 > len(playlistarray['playlists'][index]['songs'])):
                        print("Not a valid song number!")
                     else:
                        del playlistarray['playlists'][index]['songs'][songname - 1]
                  except ValueError:
                     print("Not valid song number!")
            except ValueError:
               print("Invalid playlist number!")
            
         elif (cmd == 'ppl'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  playlistfuncs.listsongs(index)
                  print("Input bellow is a scale so e.g: 1-5 means form song 1 to 5. Put the same number twice to play 1 song. E.g: 1-1 means play song 1")
                  songs = input("Input songs > ").replace(" ", "")
                  songs = songs.split('-')
                  if (len(songs) > 2):
                     print("Invalid range!")
                  else:
                     try:
                        songs[0] = int(songs[0])
                        songs[1] = int(songs[1])

                        if (songs[0] > songs[1]):
                           print("Invalid range!")
                        else:
                           if (songs[0] < 1 or songs[1] > len(playlistarray['playlists'][index]['songs'])):
                              print("Invalid range")
                           else:
                              ara = ""

                              if (songs[0] == songs[1]):
                                 doplay(playlistarray['playlists'][index]['songs'][songs[0] - 1]['url'])
                              else:
                                 for i in range(songs[1] - songs[0] + 1):
                                    ara += playlistarray['playlists'][index]['songs'][i + songs[0] - 1]['url']
                                    ara += " "
                                 doplay(ara)  
                     except ValueError:
                        print("Invalid range!")
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'rps'):
            playstring = ""
            tmparray = playlistarray['playlists'][index]['songs']
            array = [0] * len(tmparray)

            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  for i in range(len(tmparray)):
                     array[i] = tmparray[i]['url']

                  random.shuffle(array)

                  for song in array:
                     playstring += song + " "
                  
                  doplay(playstring)
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'rls'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")
            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  del playlistarray['playlists'][index]
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'lss'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  playlistfuncs.listsongs(index)
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'lsp'):
            playlistfuncs.listplaylists()

         elif (cmd == 'rar'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  playlistfuncs.listsongs(index)
                  print("Input bellow is a scale so e.g: 1-5 means move song 1 to position 5 and song 5 to position 1")
                  songs = input("Input songs > ").replace(" ", "")
                  songs = songs.split('-')
                  if (len(songs) > 2):
                     print("Invalid range!")
                  else:
                     try:
                        songs[0] = int(songs[0])
                        songs[1] = int(songs[1])

                        if (songs[0] < 1 or songs[1] > len(playlistarray['playlists'][index]['songs'])):
                           print("Invalid range")
                        else:
                           latterindex = playlistarray['playlists'][index]['songs'][songs[1] - 1]
                           formerindex = playlistarray['playlists'][index]['songs'][songs[0] - 1]

                           playlistarray['playlists'][index]['songs'][songs[1] - 1] = formerindex
                           playlistarray['playlists'][index]['songs'][songs[0] - 1] = latterindex
                     except ValueError:
                        print("Invalid range!")
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'lppl'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  ara = ""
                  for i in range(len(playlistarray['playlists'][index]['songs'])):
                     ara += playlistarray['playlists'][index]['songs'][i]['url']
                     ara += " "
                  doplayloop(ara)  
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'lplo'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  playlistfuncs.listsongs(index)
                  sindex = input("Input song index >")
                  try:
                     sindex = int(index) -1
                     if (sindex < 1 or sindex > len(playlistarray['playlists'][index]['songs'])):
                        print("Invalid song!")
                     else:
                        doplayloop(playlistarray['playlists'][index]['songs'][sindex]['url']) 
                  except ValueError:
                     print("invalid input") 
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'lspl'):
            playlistfuncs.listplaylists()
            index = input("Input playlist name > ")

            try:
               index = int(index) -1
               if (index > len(playlistarray['playlists'])):
                  print("Invalid playlist number!")
               else:
                  ara = ""
                  for i in range(len(playlistarray['playlists'][index]['songs'])):
                     ara += playlistarray['playlists'][index]['songs'][i]['url']
                     ara += " "
                  doplayloopshuffle(ara) 
            except ValueError:
               print("Invalid playlist number!")

         elif (cmd == 'lp'):
            if (dotestmusic): dostopmusic()

            try:
               doplayloop(resarray[int(cmdinput[1]) - 1])
            except IndexError:
               try:
                  inp1 = input("Input video number > ")
                  inp = resarray[int(inp1) - 1]

                  doplayloop(inp)
               except IndexError:
                  print("No such video!")
            except ValueError:
               print("Invalid number!")
            except NameError:
               print("You have not searched anything yet!")

         elif (cmd == 'ifl'):
            if (len(cmdinput) > 1):
               del cmdinput[0]
               tmpresarray = dosearchyt(' '.join(cmdinput), 1)
               doplay(tmpresarray['urls'][0])
            else:
               inp = input("Input search term > ")
               
               if (inp != ""):
                  tmpresarray = dosearchyt(inp, 1)
                  doplay(tmpresarray['urls'][0])
               else:
                  print("Nothing searched!")

         elif (cmd == 'vi'):
            if (videobool):
               videobool = False
            else:
               videobool = True

         else:
            print(cmd + ": Invalid command!")
      except KeyboardInterrupt:
         print("\n")

def doprintsearchinfo():
   i = 0
   tw = int(terminal_size()[0])

   try:
      for i in range (len(titlearray)):
         formated = '%-{a}s %-{b}s %-{c}s %-{d}s'.format(a=int(tw*0.54), b=int(tw*0.2), c=int(tw*0.13), d=int(tw*0.10))

         print(i+1, end='')
         print('. ' + formated % (titlearray[i], channelarray[i], viewarray[i], durationarray[i]))
   except NameError:
      print("Nothing searched!")

def doserialize(inp):
   return json.dumps(inp, indent=3)

def dodeserialize(inp):
   return json.loads(inp)

def dohelp():
   keys = ["h", "s", "i", "q", "?", "/", "p", "v", "r", "npl", "pls", "dls", "ppl", "rps", "rls", "lss", "lsp", "rar", "lppl", "lplo", "lspl", "lp", "ifl", "vi"]
   func = ["Print this help list", "Stop current song", "Print current info about current song and music stack", "Exit the program",
   "Search for a specific term and add the results to the stack", "Same as ? (Search for song. Add to stack)", "Play song from search",
   "Set volume in percent ", "Set result amount (Warning more results = slower search)", "Add a new playlist", "Add song to playlist", "Remove song from playlist",
   "Play playlist in linear fashion.", "Play playlist in random order", "Delete playlist", "List songs in playlist", "List playlists", "Rearrange playlists",
   "Loop playlist linearly", "Loop individual song in playlist", "Loop playlist in random order",
   "Loop song from search", "I'm felling lucky serach. seacrh and play the first result", "Toggle video"]
   args = ["NONE", "NONE", "NONE", "NONE", "Search term (String)", "Search term (String)", "Number of song (Int)", "Int (0 - 100)", "Int",
   "Name (String)", "NONE (Hit enter and it will prompt you)", "NONE (Hit enter and it will prompt you)", "NONE (Will prompt you)", "NONE (Will prompt you)", 
   "NONE (Will prompt you)", "NONE (Will prompt you)", "NONE", "NONE (Will be prompted)", "NONE (Will be prompted)", "NONE (Will be prompted)",
   "NONE (Will be prompted)", "Number of song (Int)", "Search term (String)", "NONE"]

   tw = terminal_size()[0]
   formated = '   %-{a}s %-{b}s %-{c}s'.format(a=int(tw*0.05), b=int(tw*0.7), c=int(tw*0.20))

   for i in range(len(keys)):
      print(formated % (keys[i], func[i], args[i]))

def dotestmusic():
   if (os.popen("ps -e | grep -i mpv") != ""):
      return True
   else:
      return False

def doplay(url):
   if (videobool):
      subprocess.Popen("nohup mpv --really-quiet --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)
   else:
      subprocess.Popen("nohup mpv --no-video --really-quiet --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)

def doplayloop(url):
   if (videobool):
      subprocess.Popen("nohup mpv --loop-playlist --really-quiet --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)
   else:
      subprocess.Popen("nohup mpv --loop-playlist --no-video --really-quiet --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)

def doplayloopshuffle(url):
   if (videobool):
      subprocess.Popen("nohup mpv --loop-playlist --really-quiet --shuffle --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)
   else:
      subprocess.Popen("nohup mpv --loop-playlist --no-video --really-quiet --shuffle --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)

def dostopmusic():
   os.system("killall mpv >/dev/null 2>&1")

def dosearchyt(query, num):
   resultarray = [0] * int(num)
   ids = [0] * int(num)
   titles = [0] * int(num)
   channels = [0] * int(num)
   durations = [0] * int(num)
   views = [0] * int(num)

   results = YoutubeSearch(query, max_results=int(num)).to_dict()


   for i in range(num):
      ids[i] = results[i]['id']
      views[i] = results[i]['views']
      titles[i] = results[i]['title']
      channels[i] = results[i]['channel']
      durations[i] = results[i]['duration']

   for i in range(int(num)): resultarray[i] = "https://www.youtube.com/watch?v=" + ids[i]

   datadict = { "urls": resultarray, "titles": titles, "views": views, "channels": channels, "durations": durations }

   return datadict

def terminal_size():
   th, tw, hp, wp = struct.unpack('HHHH',
      fcntl.ioctl(0, termios.TIOCGWINSZ,
      struct.pack('HHHH', 0, 0, 0, 0)))
   return tw, th

def readandcheckconfig():
   global playlistarray
   global downloadarray

   try:
      f = open("playlists.json")
      b = open("downloads.json")

      try:
         playlistarray = dodeserialize(f.read())
         downloadarray = dodeserialize(b.read())
      except decoder.JSONDecodeError:
         playlistarray = playlistfuncs.newplaycollection()
         downloadarray = None

   except IOError:
      print("Welcome to music player.py!\nThis is either your first time using the\nprogram or you have deleted your playlist config file\nBy typing \"OK\", \"Yes\" or \"y\" you agree to let this program\nwrite to your disk.\nDo you accept?\n")
      confirm = input("Type \"OK, y or yes\" to agree: ")
      
      if (confirm.lower() == "y" or confirm.lower() == "yes" or confirm.lower() == "ok"):
         f = open("playlists.json", "w+")
         b = open("downloads.json", "w+")

         playlistarray = playlistfuncs.newplaycollection()
         downloadarray = None

         f.close()
         b.close()

         os.mkdir("py-music-downloads")
      else:
         exit()

def doexit():
   clear()
   print("\nExiting")

   if (dotestmusic): dostopmusic()

   open("playlists.json", "w").close()
   open("downloads.json", "w").close()

   f = open("playlists.json", "w+")
   b = open("downloads.json", "w+")

   f.write(doserialize(playlistarray))
   b.write(doserialize(downloadarray))

   f.close()
   b.close()

   print("Goodbye!")
   exit()

def clear():
   if (clearbool):
      os.system('clear')
   elif (clearbool == False):
      pass

def setupparser():
   global volume
   global results
   global clearbool
   global videobool

   parser = argparse.ArgumentParser()

   parser.add_argument('--noclear', action='store_true', help="Prevent musicplayer.py from clearing console")
   parser.add_argument('--version', '-V', action='store_true', help="Print version and exit")
   parser.add_argument('--video', action='store_true', help="Set video on")

   parser.add_argument('--volume', '-v', default=100, help="Set initial volume in percent (Default 100)")
   parser.add_argument('--results', '-r', default=3, help="Set initial amount of results (Default 3)")

   args = parser.parse_args()

   if (args.version):
      print(version)
      exit()

   if (args.noclear):
      clearbool = False
   else:
      clearbool = True

   if (args.video):
      videobool = True
   else:
      videobool = False

   results = int(args.results)
   volume = int(args.volume)

   if (int(volume) < 101 and int(volume) > -1):
      pass
   else:
      print("Volume: arg too big/small!")
      exit()
      
   if (int(results) > 0):
      pass
   else:
      print("Results: too small!")
      exit()

def main():
   try:
      readandcheckconfig()
      setupparser()
      mainloop()

   except KeyboardInterrupt:
      doexit()

if __name__ == "__main__":
   main()