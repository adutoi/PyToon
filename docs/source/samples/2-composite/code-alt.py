from pytoon import composite, line, circle

my_circle = circle(radius=100, lstyle=False, fstyle="salmon")

composite([
    line(begin=(-150,0), end=(+150,0), lstyle=(10,"#0000FF")),
    my_circle(center=(-30,0)),
    my_circle(center=(+30,0), fstyle="0.8 * green")
]).svg("two-circles-alt")
