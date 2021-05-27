import swi

def vdu(*args):
    for arg in args:
        swi.swi('OS_WriteC', 'i', arg)

def set_rgb(r,g,b,action=0,background=False):
    entry = b << 24 | g << 16 | r << 8
    flags = 0x80 if background else 0
    swi.swi('ColourTrans_SetGCOL','I..II', entry, flags, action)

Move       = 0
Foreground = 1
Inverse    = 2
Background = 3


def plot(cmd, pos, action=Foreground, relative=False):
    if not relative:
        action = action+4
    x,y = pos
    swi.swi('OS_Plot','iii',cmd+action, int(x), int(y))

def plots(cmd, *points, action=Foreground, relative=False):
    first = True
    for point in points:
        if first:
            plot(cmd, point, action=action, relative=False)
        else:
            plot(cmd, point, action=action, relative=relative)

def line(a, b, action=Foreground, relative=False):
    plot( 0, a, action=Move,   relative=False    )
    plot( 0, b, action=action, relative=relative )

def point( p ):
    plot( 64, p )

def triangle(a, b, c, fill=False):
    if fill:
        plot( 80, a, Move )
        plot( 80, b, Move )
        plot( 80, c )
    else:
        plots( (4,a), (5,b), (5,c), (5,a) )

def rectangle(pos, pos2=None, width=None, height=None, fill=False):
    if pos2 is not None:
        width  = pos2[0] - pos[0]
        height = pos2[1] - pos[1]
    x,y = pos
    if height is None:
        height = width
    plot(0, pos, Move)
    if fill:
        plot(96, (x+width, y+height))
    else:
        plot(0, (x+width, y))
        plot(0, (x+width, y+height))
        plot(0, (x, y+height))
        plot(0, pos)

def square(pos, size, fill=False):
    rectangle(pos, width=size, height=size, fill=fill)

def parallelogram(a, b, c, fill=False):
    if fill:
        plots( (4,a), (4,b), (117,d) )
    else:
        plots( (4,a), (5,b), (5,c), (5, (a[0]+(c[1]-b[1]), a[1]) ) )

def circle(centre, radius, fill=False):
    plot( 0, centre, Move)
    plot( 152 if fill else 144, (centre[0]+radius, centre[1]) )

def arc(centre, start, end):
    plot( 160, centre, Move )
    plot( 160, start,  Move )
    plot( 160, end )

def segment(centre, start, end):
    plots( (4,centre), (4,start), (163,end) )

def sector(centre, start, end):
    plot( 176, centre, Move )
    plot( 176, start,  Move )
    plot( 176, end )

def ellipse(centre, man, min, fill=False):
    plots( (4, centre), (4, (a[0]+maj,a[1])),
           (205 if fill else 199, (a[0], a[1]+min)) )

def fill(point):
    plot( 141, point )
