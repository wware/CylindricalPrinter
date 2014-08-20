import("/Users/wware/CylindricalPrinter/early_prototype/Hollow_Dodecahedron.stl");

for (i = [0:2])
rotate(i * 144, [0,0,1])
translate([0, 30, -20])
cylinder(h=20, r1=5, r2=1, $fn=6);