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

DIRECTIONS = enumerate([[ 1, 0, 0],
              [-1, 0, 0],
              [ 0, 1, 0],
              [ 0,-1, 0],
              [ 0, 0, 1],
              [ 0, 0,-1]])



# get_next_index() controls the function of the algorithm
#   return l-1 --> Recursive Backtracker
#   return random(0,l-1) --> Prim's
#   can do other combinations of the two to get different results
def get_next_index(l):
    return l-1

# return True if the block in on the edge of the 3D maze,
#   that is not on its interior or outside
def valid_cell(x,y,z):
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

# messy wrapping code that does the wrapping of the maze around the 3d cube
def wrap(x,y,z):
    if x < 0:
        if z == 0:              return (x+1,y  ,z+1)
        elif z == DEPTH-1: return (x+1,y  ,z-1)
        elif y == 0:            return (x+1,y+1,z  )
        elif y == HEIGHT-1:return (x+1,y-1,z  )
    elif x >= WIDTH:
        if z == 0:              return (x-1,y  ,z+1)
        elif z == DEPTH-1: return (x-1,y  ,z-1)
        elif y == 0:            return (x-1,y+1,z  )
        elif y == HEIGHT-1:return (x-1,y-1,z  )
    elif y < 0:
        if z == 0:              return (x,  y+1,z+1)
        elif z == DEPTH-1: return (x,  y+1,z-1)
        elif x == 0:            return (x+1,y+1,z  )
        elif x == WIDTH-1: return (x-1,y+1,z  )
    elif y >= HEIGHT:
        if z == 0:              return (x,  y-1,z+1)
        elif z == DEPTH-1: return (x,  y-1,z-1)
        elif x == 0:            return (x+1,y-1,z  )
        elif x == WIDTH-1: return (x-1,y-1,z  )
    elif z < 0:
        if x == 0:              return (x+1,y  ,z+1)
        elif x == WIDTH-1: return (x-1,y  ,z+1)
        elif y == 0:            return (x,  y+1,z+1)
        elif y == HEIGHT-1: return (x, y-1,z+1)
    elif z >= DEPTH:
        if x == 0:              return (x+1,y  ,z-1)
        elif x == WIDTH-1: return (x-1,y  ,z-1)
        elif y == 0:            return (x,  y+1,z-1)
        elif y == HEIGHT-1:return (x, y-1,z-1)

# Prints out the zth layer of the maze to the console
def printMazeLayer(z):
    for y in range(HEIGHT):
        linestr = ""
        for x in range(WIDTH):
            if grid[0][y][x] == "#":
                linestr += "# "
            else:
                linestr += "  "
        print linestr

def generateSCAD():
    print "converting 3D maze into OpenSCAD model: ", OUTPUT_FILE_NAME
    with open(OUTPUT_FILE_NAME,'w') as f:
        f.write("size = 1; //CHANGE TO RESIZE THE OBJECT!\n")
        f.write("w = 0.1;\n")

        # ''' 3D maze as one part
        f.write("module maze() {\n")
        f.write("\tunion() {\n")
        for z in range(DEPTH):
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if grid[z][y][x] == "#":
                        f.write("\t\ttranslate(["+str(x)+", "+str(y)+", "+str(z)+"]) cube(1);\n")
        f.write("\t}\n")
        f.write("}\n")
        f.write("color([1,0,0]) maze();")
        # '''

    print "finished!"


class Cell:

    def __init__(self):
        self.connected = [False,False,False,False,False,False]
        self.touched = False

    def is_untouched(self):
        return self.touched == False

    def mark(self, i):
        self.connected[i] = True
        self.touched = False

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

    random.shuffle(DIRECTIONS)
    for i,d in DIRECTIONS[1]:
        (nx,ny,nz) = (x+d[0], y+d[1], z+d[2])
        if not valid_cell(nx,ny,nz):
            (nx,ny,nz) = wrap(nx,ny,nz)
            if grid[nz][ny][nx].is_untouched():
                grid[x][y][z].mark(i)
                grid[nx][ny][nz].mark(Cell.opposite(i))
                cells.append((nx,ny,nz))
                index = None
                break

    if index != None: 
        del cells[index]

generateSCAD()
#printMazeLayer(0)
