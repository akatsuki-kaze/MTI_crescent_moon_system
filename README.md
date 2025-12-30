# MTI_crescent_moon_system——MCMS
## what about this system
this is a easy robot control program. It was developed on [MTI_volleyball_opensource](https://github.com/akatsuki-kaze/MTI_volleyball_opensource),complete build on python. After some simplify and optimize,I decide to release our system on the volley ball robot.Even this program based on Serial,but I think someone who is able to develop more function instead of Serial,such as can bus.
## How to use
As you see ,this program has three parts. ```basic_functional```,```HAL```and```image_dection```are three kinds of functional.```basic_functional```include some basic algorithm like pid.```HAL```have some program to help you use hardware easier.While```image_detection```include some image process.You can use your own main.py to use these package.
```
from HAL import depth_camera as cam
```
just like this.

