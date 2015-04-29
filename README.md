dungeoneer
==========

Simple RogueLike based on great tutorial at:
http://roguebasin.roguelikedevelopment.org/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod

Uses libtcod

To use, download this code and follow the instructions in the tutorial for setting up python 2.7 and libtcod 1.5.1

namely, put SDL.dll and libtcod-mingw.dll in the same directory as the .py and .png files

on linux, get libtcod 1.5.1 via:
wget -O libtcod-1.5.1_linux_64bit.tar.gz http://roguecentral.org/doryen/?file_id=28
tar -vxzf libtcod-1.5.1_linux_64bit.tar.gz

mv libtcodpy.py libtcodpy-win.py
cp libtcod-1.5.1/libtcodpy.py ./
cp libtcod-1.5.1/terminal.png ./

sudo apt-get install libsdl1.2debian

in data.py set ASCIIMODE to True and GRAPHICSMODE to False

To move, use arrow keys, num pad, or hjklyubn

Pick up items with 'g'

Check character status with 'c'

Open the Inventory with 'i'

Drop items with 'd'

Go down the stairs with '>' (you can't come back up!)



There's a few other super secret debug keys as well!

a and q show the map and all enemies
z will put you on the next floor
x is an instant level-up
w will give all items



