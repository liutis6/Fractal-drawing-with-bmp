# Description:
Python program for creating an image of a recursive pattern using a BMP file.
Two use cases:
    1. a depth is given - the program resizes the image to fit the fractal.
    2. a pixel width is given - fractal stop drawing as soon as it reaches the specified width.

Lots of comments as this is all new to me.

# Instructions (***subject to change***):
* Implement function according to use case
* Run "main.py"

# Structure (***subject to change***):
* main.py - the entire program
* output.bmp - gotten result
* images - images for showcasing in readme

# Todo (***subject to change***): 
* BMP file printing template
* Recursive algorithm for pattern
* Dynamic file size resizing
* Stopping program when at given width
* Input error protection
* Testing
* Benchmarking

## Pattern to replicate (Minkowski Sausage):
![pattern](images/pattern.png "pattern")

## Example output
* depth = 6,  line_len = 3:
![depth6](images/d6.png "depth6")

* depth = 3, line_len = 3
![depth3](images/d3.png "depth3")


## References:
- Inspiration for the recursion function: https://github.com/spirometaxas/minkowski-sausage-cli
- Definition: https://en.wikipedia.org/wiki/Minkowski_sausage