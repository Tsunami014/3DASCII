import math
import readchar
import BlazeSudio.collisions as colls

TILESIZE = 100
DISPLAYSIZE = (60, 30)
VIEWDIST = 500
FOV = 100

def renderTilemap(map):
    split = map.split('\n')
    out = []
    start = [0, 0]
    for row in range(len(split)):
        for col in range(len(split[row])):
            val = split[row][col]
            if val == '#':
                out.append(colls.Rect(row*TILESIZE, col*TILESIZE, TILESIZE, TILESIZE, 0))
            elif val == 'S':
                start = [row+0.5, col+0.5]
    return colls.ShapeCombiner.combineRects(*out), start

def printWorld(blocks, pos, angle):
    pos = (pos[0] * TILESIZE, pos[1] * TILESIZE)
    grid = [[" "]*DISPLAYSIZE[0] for _ in range(DISPLAYSIZE[1])]
    for x in range(DISPLAYSIZE[0]):
        endPos = colls.rotate(pos, (pos[0], pos[1]-VIEWDIST), angle+((x - DISPLAYSIZE[0]/2)*(FOV/DISPLAYSIZE[0])))
        ray = colls.Line(pos, endPos)
        cs = [i for i in blocks if i.collides(ray)]
        wheres = [j for i in cs for j in ray.whereCollides(i)]
        if len(wheres) != 0:
            wheres.sort(key=lambda p: (p[0]-pos[0])**2 + (p[1]-pos[1])**2)
            p = wheres[0]
            dist = math.sqrt((p[0]-pos[0])**2 + (p[1]-pos[1])**2)
            #c = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'."[int((dist/VIEWDIST)*50)]
            d = (p[0]-pos[0], p[1]-pos[1])
            ts = [i.tangent(colls.Point(*p), d) for i in cs]
            c = {0: ".", 45: ",", 90: ":", 135: ";", 180: "'", 180+45: '"', 270: "[", 270+45: "]"}[ts[0]%360]
            diff = int((dist/VIEWDIST) * (DISPLAYSIZE[1]/2))
            for y in range(DISPLAYSIZE[1]-diff*2):
                grid[y+diff][x] = c
    
    for col in grid:
        print("".join(col))
    
    print("\n\033[%iD"%DISPLAYSIZE[0], end='')

angle = 0
blocks, pos = renderTilemap("""
##########
##   #   #
# S ###  #
#    #  ##
###    # #
# #  #   #
#  # # # #
##########
""")

print("\n"*DISPLAYSIZE[1], end='')
while True:
    print('\033[%iA'%(DISPLAYSIZE[1]+1), end='')
    printWorld(blocks, pos, angle)
    o = readchar.readkey()
    move = [0, 0]
    if o == 'w' or o == readchar.key.UP:
        move[1] -= 0.1
    if o == 's' or o == readchar.key.DOWN:
        move[1] += 0.1
    if o == 'a':
        move[0] -= 0.1
    if o == 'd':
        move[0] += 0.1
    opos = pos.copy()
    pos[0] += move[0]*math.cos(math.radians(angle)) - move[1]*math.sin(math.radians(angle))
    pos[1] += move[0]*math.sin(math.radians(angle)) + move[1]*math.cos(math.radians(angle))
    if colls.Line(opos, pos).collides(blocks):
        pos = opos
    if o == 'q' or o == readchar.key.LEFT:
        angle -= 5
    if o == 'e' or o == readchar.key.RIGHT:
        angle += 5
