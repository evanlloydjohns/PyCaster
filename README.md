# PyCaster [WIP]

_Welcome to my little hobby corner of the Internet!_

I've been interested in rendering engines and physics simulations for quite some time now, and I wanted to sit down and give it a go my self. This project is something I have been slowly working on for the past year, and is an outlet for me to experiment with the thought processes required in designing one's own game engine. 

I originally started this project in Java, but decided that It would be better to prototype the idea in python with pygame, and then move to Java (or hopefully C some day) once the general concepts and overall structure is down. 

### A Ray Caster?!...

Most ray casters you'll find online use a grid based system, where the world is separated into cells which can be occupied by different states (a wall with a brick texture, a wall with a metal textue, a door, etc.). This is a really effective and efficient approach, but it does limit flexability in world geometry. 

That's where this ray caster differs. I was originally captivated by the concept of raycasting after seeing demos similar to the one seen [here](https://www.youtube.com/watch?v=58l0SURwYpc). I really enjoyed the idea being able to place walls at any location and orientation. I could also see how the implementation of more complex geometry wouldn't be too difficult once the core structure was put in place. This led me to start work on a more traditional pseudo 3D ray caster with support for more complex world shapes and on the fly object creation.

That is not to say that this has never been done before (as it has, many times). Instead, this is just meant to be a fun project to help me solidify concepts, data structures, and mathematical concepts I've learned over the past four years.

This project is currently in it's infant state, as I work out bugs and add more features. My goal is to have two executables, a world editor, and a ray caster. The world editor will have tools that allow you to create levels, and the ray caster will be the engine that can render those levels. Once the ray caster gets to a good state, I'll start work on the world editor.


## Examples

![](resources/demo_images/demo_03.png)
![](resources/demo_images/demo_02.png)
![](resources/demo_images/demo_01.png)
![](resources/demo_images/demo_04.png)

You can view a demo video [here](https://youtu.be/N-VxHK4egNw)

## Installation

Clone this repo to a folder

```commandline
git clone https://github.com/CutlassS1968/PyCaster.git
```

Install pygame
```commandline
pip install pygame
```

run the ray caster
```commandline
python ./game.py
```

If you want to change the map, you can create and save a new map using the Map Builder
```commandline
python ./builder.py
```

If you need to change any settings, they are located in the settings.ini file

## Future tasks

This is just a collection of various notes I've written while working on the project. Some of these are outdated and are no longer relevant to the project.

To-do's:
- [x] Add another world object type
- [x] Lay groundwork for texture mapping
- [x] Add rudimentary player collision for world objects
- [x] De-link world coordinate system from window dimensions
- [x] Formalize a world objects data structure for future additions
- [x] Reformat engine and game initialization to better support OOP principles
- [x] Add broad-phase collision selection for walls
- [x] Add a GUI module for implementation of a start menu and pause menu
- [ ] Investigate migrating mouse button input to engine.process_mouse_buttons()
- [ ] Add config for variable graphics modules (maybe class that handles controls depending on module)
- [ ] Investigate the use of a decorator for the player collision check
- [ ] Need to make mouse movement smooth
- [x] Allow player to slide along wall (do some trig stuff I guess)
- [ ] There's a pretty big issue right with what seems like a memory leak of some kind.


Large Goals:
- [x] Add a legitimate ReadMe!
- [x] Add better documentation (Seriously, document your code)
- [x] Optimize calculations by dynamically selecting walls/rays
- [ ] Further investigate more efficient ways of calculating collisions
- [ ] Add dynamic texture mapping to world objects
- [x] Add menu system
- [x] Add loading and saving of world states
- [ ] Add entities
- [ ] Add more propper floors/ceilings
- [ ] Switch to a more efficient graphics module
- [x] Create a world editor

