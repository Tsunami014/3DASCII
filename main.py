from getch import GetCh
c = GetCh()
while True:
    print("HI", c())
print("\\033[2K                          - Clear Line")
print("\\033[<N>A                        - Move the cursor up N lines")

TILESIZE = 100

x, y, a = [int(i) for i in input().split()]
grid = []
for i in range(int(input())):
    grid.append(input())
