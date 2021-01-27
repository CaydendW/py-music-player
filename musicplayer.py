try:
   import os
   import json
   import fcntl
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
            break
         else:
            pass
      return False

class cheeckygoto(Exception):
   pass

def mainloop():
   global resarray
   global titlearray
   global durationarray
   global viewarray
   global channelarray
   global currplay
   global volume
   global results

   clear()

   while True:
      try:
         cmdinput = input("Music-cmd > ")
      except EOFError:
         doexit()

      clear()

      cmdinput = cmdinput.split(' ')
      cmd = cmdinput[0]

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
         else:
            inp = input("Input search term > ")

            if (inp != ""):
               tmpresarray = dosearchyt(inp, results)
               
               resarray = tmpresarray['urls']
               titlearray = tmpresarray['titles']
               channelarray = tmpresarray['channels']
               viewarray = tmpresarray['views']
               durationarray = tmpresarray['durations']
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
         else:
            inp = input("Input search term > ")
            
            if (inp != ""):
               tmpresarray = dosearchyt(inp, results)
               
               resarray = tmpresarray['urls']
               titlearray = tmpresarray['titles']
               channelarray = tmpresarray['channels']
               viewarray = tmpresarray['views']
               durationarray = tmpresarray['durations']
            else:
               print("Nothing searched!")

      elif (cmd == 'p'):
         if (dotestmusic): dostopmusic()

         currplay = ""

         try:
            currplay = titlearray[int(cmdinput[1]) - 1]

            doplay(resarray[int(cmdinput[1]) - 1])
         except IndexError:
            try:
               inp1 = input("Input video number > ")
               inp = resarray[int(inp1) - 1]

               currplay = titlearray[int(inp1) - 1]

               doplay(inp)
            except IndexError:
               print("No such video!")
         except NameError:
            print("You have not searched anything yet!")

      elif (cmd == 'i'):
         i = 0
         tw = int(terminal_size()[0])

         try:
            if (currplay == "" or dotestmusic() == False):
               print("Nothing playing\n")
            else:
               print("Now playing: " + currplay)
         except NameError:
            print("Nothing playing\n")

         try:
            for i in range (len(titlearray)):
               formated = '%-{a}s %-{b}s %-{c}s %-{d}s'.format(a=int(tw*0.54), b=int(tw*0.2), c=int(tw*0.13), d=int(tw*0.10))

               print(i+1, end='')
               print('. ' + formated % (titlearray[i], channelarray[i], viewarray[i], durationarray[i]))
         except NameError:
            print("Nothing searched!")
      
      elif (cmd == 's'):
         currplay = ""
         dostopmusic()

      elif (cmd == 'v'):
         if (int(cmdinput[1]) > 100 or int(cmdinput[1]) < 0):
            print("Invalid input. Number too big/small")
         else:
            volume = int(cmdinput[1])
      
      elif (cmd == 'r'):
         if (int(cmdinput[1]) > 5):
            x = input("Are you sure you would like to make it this big. y/n: ")
            if (x.lower() == 'y'):
               results = int(cmdinput[1])
            else:
               pass
         elif (int(cmdinput[1]) > 1 and int(cmdinput[1]) < 6):
            results = int(cmdinput[1])
         elif (0 >= int(cmdinput[1])):
            print("Number too small")
      
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

               f = open("playlists.json", "w")
               f.write(doserialize(playlistarray))
               f.close()
         except cheeckygoto:
            print("Invalid name!")

      elif (cmd == 'pls'):
         global index

         try:
            plname = input("Input playlist name > ")
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

      else:
         print(cmd + ": Invalid command!")

def doserialize(inp):
   return json.dumps(inp, indent=3)

def dodeserialize(inp):
   return json.loads(inp)

def dohelp():
   keys = ["h", "s", "i", "q", "?", "/", "p", "v", "r", "npl", "pls"]
   func = ["Print this help list", "Stop current song", "Print current info about current song and music stack", "Exit the program",
   "Search for a specific term and add the results to the stack", "Same as ? (Search for song. Add to stack)", "Play Song",
   "Set volume in percent ", "Set result amount (Warning more results = slower search)", "Add a new playlist", "Add song to playlist"]
   args = ["NONE", "NONE", "NONE", "NONE", "Search term (String)", "Search term (String)", "Number of song (Int)", "Int (0 - 100)", "Int",
   "Name (String)", "NONE (Hit enter and it will prompt you)"]

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