from pytoon import composite, line, circle

sub_image = composite([
    line(begin=(-150,0), end=(+150,0), lstyle=("WEIGHT","#0000FF")),
    circle(center=(-30,0), radius=100, lstyle=False, fstyle="salmon"),
    circle(center=(+30,0), radius=100, lstyle=False, fstyle="GREEN")
])

image = composite([
    sub_image(GREEN="0.1*green"),
    sub_image(GREEN="0.2*green").T(  0, 110),
    sub_image(GREEN="0.3*green").T(  0, 220),
    sub_image(GREEN="0.4*green").T(300,   0),
    sub_image(GREEN="0.5*green").T(300, 110),
    sub_image(GREEN="0.6*green").T(300, 220),
    sub_image(GREEN="0.7*green").T(600,   0),
    sub_image(GREEN="0.8*green").T(600, 110),
    sub_image(GREEN="0.9*green").T(600, 220)
], WEIGHT=30).R(20)

image.svg()
