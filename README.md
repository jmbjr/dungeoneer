dungeoneer
==========

Simple RogueLike based on great tutorial at:
http://roguebasin.roguelikedevelopment.org/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod

Uses libtcod.  Currently this repo packages the libtcod python files along with the linux/osx/win libraries.

Location to download the libraries and py files yourself (you can get the source there as well):
http://roguecentral.org/doryen/libtcod/download/

To use, download this code and follow the instructions in the tutorial for setting up python 2.7 and libtcod 1.5.1 (shouldn't be any work to do since the repo handles this for you)

on linux you'll probably need to install libsdl1:

sudo apt-get install libsdl1.2debian

the .so file is the 64bit one by default. you may want to copy over the 32bit one if needed.

You can set some options in data.py to tweak the game.  

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



