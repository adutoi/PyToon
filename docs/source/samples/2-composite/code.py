from pytoon import composite, line, circle

composite([
    line(begin=(-150,0), end=(+150,0), lstyle=(3,"#A0522D")),
    circle(center=(-30,0), radius=100, lstyle=False, fstyle="salmon"),
    circle(center=(+30,0), radius=100, lstyle=False, fstyle="0.8 * green")
]).svg("two-circles")
