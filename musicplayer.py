try:
   import os
   import json
   import fcntl
   import struct
   import termios
   import argparse
   import subprocess

   from youtube_search import YoutubeSearch
except ImportError as e:
   print("Not all dependencies have been installed! Exiting!")
   exit()

version = "0.0.1"

cmdinput = None
f = None
playarray = None
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
      print("Music-cmd > ", end="")
      cmdinput = input()

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

      else:
         print("Invalid command!")

def doserialize(inp):
   return json.dumps(inp, indent=3)

def dodeserialize(inp):
   return json.loads(inp)

def dohelp():
   keys = ["h", "s", "i", "q", "?", "/", "p", "v", "r"]
   func = ["Print this help list", "Stop current song", "Print current info about current song and music stack", "Exit the program",
   "Search for a specific term and add the results to the stack", "Same as ? (Search for song. Add to stack)", "Play Song",
   "Set volume in percent ", "Set result amount (Warning more results = slower search) "]
   args = ["NONE", "NONE", "NONE", "NONE", "Search term (String)", "Search term (String)", "Number of song (Int)", "Int (0 - 100)", "Int"]

   tw = terminal_size()[0]

   for i in range(len(keys)):
      formated = '   %-{a}s %-{b}s %-{c}s'.format(a=int(tw*0.05), b=int(tw*0.7), c=int(tw*0.20))
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
   resultarray = [0] * num
   ids = [0] * num
   titles = [0] * num
   channels = [0] * num
   durations = [0] * num
   views = [0] * num

   results = YoutubeSearch(query, max_results=num).to_dict()


   for i in range(num):
      ids[i] = results[i]['id']
      views[i] = results[i]['views']
      titles[i] = results[i]['title']
      channels[i] = results[i]['channel']
      durations[i] = results[i]['duration']

   for i in range(num): resultarray[i] = "https://www.youtube.com/watch?v=" + ids[i]

   datadict = { "urls": resultarray, "titles": titles, "views": views, "channels": channels, "durations": durations }

   return datadict

def terminal_size():
   th, tw, hp, wp = struct.unpack('HHHH',
      fcntl.ioctl(0, termios.TIOCGWINSZ,
      struct.pack('HHHH', 0, 0, 0, 0)))
   return tw, th

def readandcheckconfig():
   try:
      f = open("playlists.json")
   except IOError:
      print("Welcome to music player.py!\nThis is either your first time using the\nprogram or you have deleted your playlist config file\nBy typing \"OK\", \"Yes\" or \"y\" you agree to let this program\nwrite to your disk.\nDo you accept?\n")
      confirm = input("Type \"OK, y or yes\" to agree: ")
      
      if (confirm.lower() == "y" or confirm.lower() == "yes" or confirm.lower() == "ok"):
         f = open("playlists.json", "w+")
         b = open("downloads.json", "w+")

         f.close()
         b.close()
      else:
         exit()

def doexit():
   clear()
   print("\nExiting")
   if (dotestmusic): dostopmusic()
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

   results = args.results
   volume = args.volume

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