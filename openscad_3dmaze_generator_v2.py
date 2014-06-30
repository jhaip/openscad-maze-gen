import random
import sys

if len(sys.argv) < 5:
    print "python openscad_3dmaze_generator.py <WIDTH> <HEIGHT> <DEPTH> <outputFileName.scad>"
    sys.exit()

WIDTH = int(float(sys.argv[1]))
HEIGHT = int(float(sys.argv[2]))
DEPTH = int(float(sys.argv[3]))
OUTPUT_FILE_NAME = sys.argv[4]

print "generating maze with cell dimensions:", WIDTH, "x", HEIGHT, "x", DEPTH

DIRECTIONS = [[ 1, 0, 0],
              [-1, 0, 0],
              [ 0, 1, 0],
              [ 0,-1, 0],
              [ 0, 0, 1],
              [ 0, 0,-1]]

def get_direction(p1,p2):
    # only of adjacent cells:
    if p2[0]-p1[0] == 1:
        return 0
    if p2[0]-p1[0] == -1:
        return 1
    if p2[1]-p1[1] == 1:
        return 2
    if p2[1]-p1[1] == -1:
        return 3
    if p2[2]-p1[2] == 1:
        return 4
    if p2[2]-p1[2] == -1:
        return 5


# get_next_index() controls the function of the algorithm
#   return l-1 --> Recursive Backtracker
#   return random(0,l-1) --> Prim's
#   can do other combinations of the two to get different results
def get_next_index(l):
    return l-1

# return True if the block in on the edge of the 3D maze,
#   that is not on its interior or outside
def valid_cell(x,y,z):
    return x>=0 and x<WIDTH and y>=0 and y<HEIGHT and z>=0 and z<DEPTH
    '''
    if x == 0 or x == WIDTH-1:
        if y >= 0 and z >= 0 and y < HEIGHT and z < DEPTH:
            return True
    if y == 0 or y == HEIGHT-1:
        if x >= 0 and z >= 0 and x < WIDTH  and z < DEPTH:
            return True
    if z == 0 or z == DEPTH-1:
        if x >= 0 and y >= 0 and x < WIDTH  and y < HEIGHT:
            return True
    return False
    '''

# messy wrapping code that does the wrapping of the maze around the 3d cube
def wrap(x,y,z):
    if x < 0:
        if z == 0:         return (x+1,y  ,z+1)
        elif z == DEPTH-1: return (x+1,y  ,z-1)
        elif y == 0:       return (x+1,y+1,z  )
        elif y == HEIGHT-1:return (x+1,y-1,z  )
    elif x >= WIDTH:
        if z == 0:         return (x-1,y  ,z+1)
        elif z == DEPTH-1: return (x-1,y  ,z-1)
        elif y == 0:       return (x-1,y+1,z  )
        elif y == HEIGHT-1:return (x-1,y-1,z  )
    elif y < 0:
        if z == 0:         return (x,  y+1,z+1)
        elif z == DEPTH-1: return (x,  y+1,z-1)
        elif x == 0:       return (x+1,y+1,z  )
        elif x == WIDTH-1: return (x-1,y+1,z  )
    elif y >= HEIGHT:
        if z == 0:         return (x,  y-1,z+1)
        elif z == DEPTH-1: return (x,  y-1,z-1)
        elif x == 0:       return (x+1,y-1,z  )
        elif x == WIDTH-1: return (x-1,y-1,z  )
    elif z < 0:
        if x == 0:         return (x+1,y  ,z+1)
        elif x == WIDTH-1: return (x-1,y  ,z+1)
        elif y == 0:       return (x,  y+1,z+1)
        elif y == HEIGHT-1:return (x, y-1,z+1)
    elif z >= DEPTH:
        if x == 0:         return (x+1,y  ,z-1)
        elif x == WIDTH-1: return (x-1,y  ,z-1)
        elif y == 0:       return (x,  y+1,z-1)
        elif y == HEIGHT-1:return (x,  y-1,z-1)
    return None

# Prints out the zth layer of the maze to the console
def printMazeLayer(z):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            print x,y,z," maze: ", grid[z][y][x].connected

template_pre1 = """//3D Maze Generated
cellWidth = 1;
wallWidth = 0.2;
bW = cellWidth+wallWidth;

"""

template_pre2 = """
bigWidth = width*bW-wallWidth; 
bigHeight = height*bW-wallWidth;
bigDepth = depth*bW-wallWidth;

module maze_structure() {
    for ( x = [0 : width-2] ) {
        translate([cellWidth+x*bW,0,0]) cube([wallWidth,bigHeight,bigDepth]);
    }
    for ( y = [0 : height-2] ) {
        translate([0,cellWidth+y*bW,0]) cube([bigWidth,wallWidth,bigDepth]);
    }
    for ( z = [0 : depth-2] ) {
        translate([0,0,cellWidth+z*bW]) cube([bigWidth,bigHeight,wallWidth]);
    }
}

module covers() {
    difference() {
        translate([-wallWidth,-wallWidth,-wallWidth]) cube([bigWidth+2*wallWidth,bigHeight+2*wallWidth,wallWidth]);
        translate([bigWidth-cellWidth,bigHeight-cellWidth,-wallWidth]) cube([cellWidth,cellWidth,wallWidth]);
    }
    difference() {
        translate([-wallWidth,-wallWidth,bigDepth]) cube([bigWidth+2*wallWidth,bigHeight+2*wallWidth,wallWidth]);
        translate([0,0,bigDepth]) cube([cellWidth,cellWidth,wallWidth]);
    }

    translate([-wallWidth,-wallWidth,-wallWidth]) cube([wallWidth,bigHeight+2*wallWidth,bigDepth+2*wallWidth]);
    translate([bigWidth,-wallWidth,-wallWidth]) cube([wallWidth,bigHeight+2*wallWidth,bigDepth+2*wallWidth]);

    translate([-wallWidth,-wallWidth,-wallWidth]) cube([bigWidth+2*wallWidth,wallWidth,bigDepth+2*wallWidth]);
    translate([-wallWidth,bigHeight,-wallWidth]) cube([bigWidth+2*wallWidth,wallWidth,bigDepth+2*wallWidth]);
}

module maze() {
"""

template_post = """
}

union() {
    difference() {
        maze_structure();
        maze();
    }
    covers();
}
""" 

def generateSCAD():
    print "converting 3D maze into OpenSCAD model: ", OUTPUT_FILE_NAME

    with open(OUTPUT_FILE_NAME,'w') as f:

        f.write(template_pre1)
        f.write("width=%s;\n" % WIDTH)
        f.write("height=%s;\n" % HEIGHT)
        f.write("depth=%s;\n" % DEPTH)
        f.write(template_pre2)

        for z in range(DEPTH):
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    for i,d in enumerate(grid[z][y][x].connected):
                        if i%2 == 0 and d == True:
                            d2 = DIRECTIONS[i]
                            xStr = "%s*bW" % x
                            yStr = "%s*bW" % y
                            zStr = "%s*bW" % z
                            if d2[0] == 1:
                                xStr += "+0.5*bW"
                            if d2[1] == 1:
                                yStr += "+0.5*bW"
                            if d2[2] == 1:
                                zStr += "+0.5*bW"
                            f.write("\ttranslate(["+xStr+","+yStr+","+zStr+"]) cube(cellWidth);\n")

        f.write(template_post)

    print "finished!"


class Cell:

    def __init__(self):
        self.connected = [False,False,False,False,False,False]
        self.touched = False

    def is_untouched(self):
        return self.touched == False

    def mark(self, i):
        self.connected[i] = True
        self.touched = True

    @staticmethod
    def opposite(i):
        return i+1 if i%2==0 else i-1

grid = [[[Cell() for x in range(WIDTH)] for y in range(HEIGHT)] for z in range(DEPTH)]
cells = []

# Growing Tree algorithm
#   Based on ruby implementation by Jamis Buck, converted to my implementation in 3D
#   http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm

(x,y,z) = (random.randint(0,WIDTH-1), random.randint(0,HEIGHT-1), 0)
cells.append((x,y,z)) # add starting cell

while len(cells) > 0:
    index = get_next_index(len(cells))
    (x,y,z) = cells[index]

    DIRECTIONS_COPY = list(DIRECTIONS)
    random.shuffle(DIRECTIONS_COPY)
    for d in DIRECTIONS_COPY:
        (nx,ny,nz) = (x+d[0], y+d[1], z+d[2])
        if not valid_cell(nx,ny,nz):
            if wrap(nx,ny,nz) != None:
                (nx,ny,nz) = wrap(nx,ny,nz)
            else:
                continue
        if grid[nz][ny][nx].is_untouched():
            i = get_direction((x,y,z),(nx,ny,nz))
            grid[z][y][x].mark(i)
            grid[nz][ny][nx].mark(Cell.opposite(i))
            cells.append((nx,ny,nz))
            index = None
            break

    if index != None: 
        del cells[index]

generateSCAD()
# printMazeLayer(0)
