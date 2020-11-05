from pytoon import composite, line, circle

my_circle = circle(radius=100, lstyle=False, fstyle="salmon")

composite([
    line(begin=(-150,0), end=(+150,0), lstyle=(3,"#A0522D")),
    my_circle(center=(-30,0)),
    my_circle(center=(+30,0), fstyle="0.8 * green")
]).svg("two-circles-alt")
