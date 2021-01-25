try:
   import os
   import json
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

def mainloop():
   global resarray
   global titlearray
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
         titlearray = [0] * results

         if (len(cmdinput) > 1):
            del cmdinput[0]
            tmpresarray = dosearchyt(' '.join(cmdinput), results)
            resarray = tmpresarray['urls']
            titlearray = tmpresarray['titles']
         else:
            tmpresarray = dosearchyt(input("Input search term > "), results)
            resarray = tmpresarray['urls']
            titlearray = tmpresarray['titles']

      elif (cmd == 'p'):
         if (dotestmusic): dostopmusic()

         currplay = ""

         try:
            currplay = titlearray[int(cmdinput[1]) - 1]

            doplay(resarray[int(cmdinput[1]) - 1])
         except IndexError:
            inp1 = input("Input video number > ")
            inp = resarray[int(inp1) - 1]

            currplay = titlearray[int(inp1) - 1]

            doplay(inp)
         except NameError:
            print("You have not searched anything yet!")

      elif (cmd == 'i'):
         i = 0

         try:
            if (currplay == ""):
               print("Nothing playing\n")
            else:
               print("Now playing: " + currplay)
         except NameError:
            print("Nothing playing\n")

         try:
            for i in range (len(titlearray)):
               print(i+1, end='')
               print(". " + titlearray[i])
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

def doserialize(inp):
   return json.dumps(inp, indent=3)

def dodeserialize(inp):
   return json.loads(inp)

def dohelp():
   print("""
   <Key>   <Function>                                                      <Args>

   h   -   Print this help list                                            NONE
   ?   -   Stop current song                                               NONE
   i   -   Print current info about current song and music stack           NONE
   q   -   Exit the program                                                NONE
   s   -   Search for a specific term and add the results to the stack     Search term (String)
   p   -   Play Song                                                       Number of song (Int)
   v   -   Set volume in percent                                           Int (0 - 100)
   r   -   Set result amount (Warning more results = slower search)        Int
   """)

def dotestmusic():
   if (os.popen("ps -e | grep -i mpv") != ""):
      return True
   else:
      return False

def doplay(url):
   subprocess.Popen("nohup mpv --no-video --really-quiet --volume=" + str(volume) + " " + url + " >/dev/null 2>&1 &", shell=True)

def dostopmusic():
   os.system("killall mpv >/dev/null 2>&1")

def dosearchyt(query, num):
   resultarray = [0] * num
   ids = [0] * num
   titles = [0] * num

   results = YoutubeSearch(query, max_results=num).to_dict()

   i = 0

   for i in range(num):
      ids[i] = results[i]['id']

   i = 0

   for i in range(num):
      titles[i] = results[i]['title']

   i = 0

   for i in range(num):
      resultarray[i] = "https://www.youtube.com/watch?v=" + ids[i]

   datadict = {
      "urls": resultarray,
      "titles": titles,
   }

   return datadict

def readandcheckconfig():
   try:
      f = open("pymusicplaylist.conf")
      playarray = f.read().split('\n')
      playarray.pop(0)
   except IOError:
      print("Welcome to music player.py!\nThis is either your first time using the\nprogram or you have deleted your playlist config file\nBy typing \"OK\", \"Yes\" or \"y\" you agree to let this program\nwrite 1 file(s) to your disk.\nDo you accept?\n")
      confirm = input("Type \"OK, y or yes\" to agree: ")
      
      if (confirm.lower() == "y" or confirm.lower() == "yes" or confirm.lower() == "ok"):
         f = open("pymusicplaylist.conf", "w+")
         f.close()
         print("Welcome new user! Type \"h\" and hit enter to see your help list\n")
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

   parser = argparse.ArgumentParser()

   parser.add_argument('--noclear', action='store_true', help="Prevent musicplayer.py from clearing console")
   parser.add_argument('--version', '-V', action='store_true', help="Print version and exit")

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
