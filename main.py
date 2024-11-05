import math
import readchar
import BlazeSudio.collisions as colls

TILESIZE = 100
DISPLAYSIZE = (60, 30)
VIEWDIST = 500
FOV = 100

IMGS = {
2: """
  #####  
 #######
#########
#########
#########
#########
 #######
  #####
""",
1: """
  #
 ##
# #
  #
#####
"""
}
IMGSZES = {
    1: 0.5
}
IMGS = {j: [i.rstrip() for i in IMGS[j].split('\n') if i.strip()] for j in IMGS}
MimgLs = {j: max(len(i) for i in IMGS[j]) for j in IMGS}
IMGS = {j: [i+" "*(MimgLs[j]-len(i)) for i in IMGS[j]] for j in IMGS}

def renderTilemap(map):
    split = map.split('\n')
    out = []
    start = [0, 0]
    renders = {"C": 1}
    for row in range(len(split)):
        for col in range(len(split[row])):
            val = split[row][col]
            if val == '#':
                out.append((colls.Rect(row*TILESIZE, col*TILESIZE, TILESIZE, TILESIZE, 0), 0))
            if val in renders.keys():
                out.append((colls.Circle(row*TILESIZE, col*TILESIZE, TILESIZE, 0), renders[val]))
            elif val == 'S':
                start = [row+0.5, col+0.5]
    return out, start # TODO: colls.ShapeCombiner.combineRects

EXTRAROWS = 1
def printWorld(blocks, pos, angle):
    pos = (pos[0] * TILESIZE, pos[1] * TILESIZE)
    def mutateShp(shape, typ):
        if typ == 1:
            SZE = IMGSZES[typ]
            p1 = colls.rotate((shape.x, shape.y), (shape.x, shape.y+shape.r*SZE), angle-90)
            p2 = colls.rotate((shape.x, shape.y), (shape.x, shape.y+shape.r*SZE), angle+90)
            return (colls.Line(p1, p2, 0), typ)
        return (shape, typ)
    blocks = [mutateShp(*i) for i in blocks]
    grid = [[" "]*DISPLAYSIZE[0] for _ in range(DISPLAYSIZE[1])]
    for x in range(DISPLAYSIZE[0]):
        endPos = colls.rotate(pos, (pos[0], pos[1]-VIEWDIST), angle+((x - DISPLAYSIZE[0]/2)*(FOV/DISPLAYSIZE[0])))
        ray = colls.Line(pos, endPos)
        cs = [i for i in blocks if i[0].collides(ray)]
        if cs:
            wheres = [(j, i) for i in cs for j in i[0].whereCollides(ray)]
            if any(wheres):
                wheres = [(i[0], i[1][0], i[1][1], (i[0][0]-pos[0])**2 + (i[0][1]-pos[1])**2) for i in wheres]
                wheres.sort(key=lambda i: i[3])
                try:
                    wheres = wheres[:[i[2] == 0 for i in wheres].index(True)+1]
                except ValueError:
                    pass
                wheres.reverse()
                for p, shp, typ, d in wheres:
                    if typ == 0:
                        dist = math.sqrt(d)
                        chrs = "@#$B&8%Z0OUCL/\\|{}[]()?-+~<>i!;:\"',."
                        c = chrs[int((dist/VIEWDIST)*len(chrs))]
                        diff = int((dist/VIEWDIST) * (DISPLAYSIZE[1]/2))
                        for y in range(DISPLAYSIZE[1]-diff*2):
                            grid[y+diff][x] = c
                    elif typ == 1:
                        dx, dy = shp.p2[0] - shp.p1[0], shp.p2[1] - shp.p1[1]
                        det = dx * dx + dy * dy
                        if det == 0:
                            continue
                        IMG = IMGS[typ]
                        SZE = IMGSZES[typ]
                        a = (dy * (p[1] - shp.p1[1]) + dx * (p[0] - shp.p1[0])) / det
                        a = int(len(IMG[0]) * (1-a))
                        dist = math.sqrt(d)
                        hei = len(IMG)+(1-dist/VIEWDIST)*DISPLAYSIZE[1]
                        hei = int(hei * SZE)
                        diff = int((DISPLAYSIZE[1]-hei)/2)
                        diff2 = len(IMG)/hei
                        for y in range(hei):
                            c = IMG[int(y*diff2)][a]
                            if c not in ("", " "):
                                grid[y+diff][x] = c
    print("\033[0;0H", end="")

    print("Hello!\033[K")

    print("\n\033[%iD"%DISPLAYSIZE[0], end='')
    for col in grid:
        print("".join(col)+"\033[K")
    
    print()

angle = -90

blocks, pos = renderTilemap("""
##########
#        #
#    C   #
#       ##
#   S  # #
#        #
#      # #
##########
""")

# blocks, pos = renderTilemap("""
# ####################
# ##   #   #         #
# #   ###  #       # #
# #    #  ##     #   #
# ###    # # #  #    #
# # #  #   #       # #
# #S                 #
# ####################
# """)

# blocks, pos = renderTilemap("""
# ##########
# ##   #   #
# # S ###  #
# #    #  ##
# ###    # #
# # #  #   #
# #  # # # #
# ##########
# """)
print("\033[2J", end="")
while True:
    printWorld(blocks, pos, angle)
    print('\033[%iA'%(DISPLAYSIZE[1]+2+EXTRAROWS), end='')
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
    if colls.Line(opos, pos).collides([i[0] for i in blocks if i[1] == 0]):
        pos = opos
    if o == 'q' or o == readchar.key.LEFT:
        angle -= 5
    if o == 'e' or o == readchar.key.RIGHT:
        angle += 5
