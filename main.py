import math
import time
import random
import readchar
import BlazeSudio.collisions as colls
from threading import Thread
from queue import Queue, Empty
t0 = time.time()

# TODO: Optimise
# TODO: Display map

TILESIZE = 100
DISPLAYSIZE = [60, 30]
VIEWDIST = 500
FOV = 100

IMGS = {
1: """
  +++++
 +#####+
+###*###+
+#*****#+
+##***##+
+#*###*#+
 +#####+
  +++++
"""
}
IMGSZES = {
    1: 0.25
}
IMGCOLS = {
    1: "\033[38;5;178m"
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
                out.append((colls.Circle((row+0.5)*TILESIZE, (col+0.5)*TILESIZE, TILESIZE, 0), renders[val]))
            elif val == 'S':
                start = [row+0.5, col+0.5]
    return out, start # TODO: colls.ShapeCombiner.combineRects

COINS = 0

def handleExtras(blocks, pos):
    pobj = colls.Point(pos[0]*TILESIZE, pos[1]*TILESIZE)
    for obj, typ in blocks.copy():
        if typ == 1:
            if obj.collides(pobj):
                global COINS
                COINS += 1
                blocks.remove((obj, typ))
    
    return blocks

def printExtras():
    return [
        f"COINS: {COINS} / {MAXCOINS}",
        "WSAD or ↑↓ to move, Q&E or ←→ to turn. F5 to exit and C to clear.",
        "JLIK to change the window size, U&O to change the FOV"
    ]

clear = True
def printWorld(blocks, pos, angle):
    pos = (pos[0] * TILESIZE, pos[1] * TILESIZE)
    def mutateShp(shape, typ):
        if typ == 1:
            random.seed(id(shape))
            off = random.randint(0, 359)
            off += (time.time() - t0) * 100
            off = int(off % 360)
            SZE = IMGSZES[typ]
            p1 = colls.rotate((shape.x, shape.y), (shape.x, shape.y+shape.r*SZE), angle-90+off)
            p2 = colls.rotate((shape.x, shape.y), (shape.x, shape.y+shape.r*SZE), angle+90+off)
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
                        chrs = "@#B&8$%Z0OUCL/\\|{}[]()?-+~<>i!;:\"',."
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
                        COL = IMGCOLS[typ]
                        a = (dy * (p[1] - shp.p1[1]) + dx * (p[0] - shp.p1[0])) / det
                        a = max(0, min(1, a))
                        a = int(len(IMG[0]) * (1-a))
                        dist = math.sqrt(d)
                        hei = len(IMG)+(1-dist/VIEWDIST)*DISPLAYSIZE[1]
                        hei = int(hei * SZE)
                        diff = int((DISPLAYSIZE[1]-hei)/2)
                        diff2 = len(IMG)/hei
                        for y in range(hei):
                            c = COL + IMG[int(y*diff2)][a] + "\033[0m"
                            if c[c.index('m')+1:-4] not in ("", " "):
                                grid[y+diff][x] = c
                        diff = int((dist/VIEWDIST) * (DISPLAYSIZE[1]/2))
                        grid[DISPLAYSIZE[1]-diff*2+diff][x] = "_"

    global clear
    if clear:
        print("\033[2J", end="")
        clear = False
    else:
        print("\033[0;0H", end="")

    displayBox = False # TODO: Options screen
    if displayBox:
        extras = printExtras()
        print("\n".join(i+"\033[K" for i in extras))

        print('╭'+'─'*DISPLAYSIZE[0]+'╮\033[K')
        for col in grid:
            print("│"+"".join(col)+"│\033[K")
        print('╰'+'─'*DISPLAYSIZE[0]+'╯\033[K')
    else:
        extras = printExtras()
        mx = max(len(i) for i in extras)
        print("┌"+"─"*mx+"┐\033[K")
        print("\n".join("│"+i+" "*(mx-len(i))+"│\033[K" for i in extras))

        if DISPLAYSIZE[0] > mx:
            print('┢'+'━'*mx+'┷'+'━'*(DISPLAYSIZE[0]-mx-1)+'┓\033[K')
        elif DISPLAYSIZE[0] < mx:
            print('┢'+'━'*DISPLAYSIZE[0]+'┱'+'─'*(mx-DISPLAYSIZE[0]-1)+'┘\033[K')
        else:
            print('┢'+'━'*mx+'┪\033[K')
        for col in grid:
            print("┃"+"".join(col)+"┃\033[K")
        print('┗'+'━'*DISPLAYSIZE[0]+'┛\033[K')
    print('\033[%iA'%(DISPLAYSIZE[1]+2+len(extras)+2), end='')

Q1 = Queue()
Q2 = Queue()
def handleInputThread(Q1: Queue, Q2: Queue):
    global pos, angle, run, clear, DISPLAYSIZE, FOV
    while True:
        o = readchar.readkey()
        Q2.put(None)
        Q1.get()
        if o == readchar.key.CTRL_C or o == readchar.key.CTRL_D or o == readchar.key.ESC or o == readchar.key.F5:
            run = False
            break
        if o == 'c':
            clear = True
        
        if o == 'j':
            DISPLAYSIZE = (DISPLAYSIZE[0]-1, DISPLAYSIZE[1])
        if o == 'l':
            DISPLAYSIZE = (DISPLAYSIZE[0]+1, DISPLAYSIZE[1])
        if o == 'i':
            DISPLAYSIZE = (DISPLAYSIZE[0], DISPLAYSIZE[1]-1)
        if o == 'k':
            DISPLAYSIZE = (DISPLAYSIZE[0], DISPLAYSIZE[1]+1)
        if o == 'u':
            FOV -= 1
        if o == 'o':
            FOV += 1

        move = [0, 0]
        if o == 'w' or o == readchar.key.UP:
            move[1] -= 0.1
        if o == 's' or o == readchar.key.DOWN:
            move[1] += 0.1
        if o == 'a':
            move[0] -= 0.1
        if o == 'd':
            move[0] += 0.1
        if move != [0, 0]:
            opos = pos.copy()
            pos[0] += move[0]*math.cos(math.radians(angle)) - move[1]*math.sin(math.radians(angle))
            pos[1] += move[0]*math.sin(math.radians(angle)) + move[1]*math.cos(math.radians(angle))
            if colls.Line((opos[0]*TILESIZE, opos[1]*TILESIZE), (pos[0]*TILESIZE, pos[1]*TILESIZE)).collides([i[0] for i in blocks if i[1] == 0]):
                pos = opos
        
        if o == 'q' or o == readchar.key.LEFT:
            angle -= 5
        if o == 'e' or o == readchar.key.RIGHT:
            angle += 5
        
        Q2.put(None)

angle = -90

tmap = """
                ######
              ###  C #
##############C  #  ##
##   # C  #       # #
# S ### #   # ##    #
#    #  #####  C# ##
###    # ##  ###  ##
#C# C#   #  C #C# # ##
#  # # #     #    #   #
#  ###########  ###C# ##
#   #  C #C  #   ####  #
##    # C #    #      #
######################
"""

tmap = tmap.strip('\n')
blocks, pos = renderTilemap(tmap)

MAXCOINS = tmap.count("C")

# blocks, pos = renderTilemap("""
# #################################
# ##   #   #       ####  #####    #
# #   ###  #       #     ###      #
# #    #  ##     # #    C #  #    #
# ###    # # #  #  # # #    # #   #
# # #  #   #       #       #      #
# #S                              #
# #################################
# """)

t = Thread(target=handleInputThread, daemon=True, args=(Q1,Q2))
t.start()

run = True
while run:
    blocks = handleExtras(blocks, pos)
    printWorld(blocks, pos, angle)
    try:
        Q2.get_nowait()
        Q1.put(None)
        Q2.get()
    except Empty:
        pass
