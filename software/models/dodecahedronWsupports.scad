// dimensions are in millimeters, half-inch-high supports
H = 18;

module dodec() {
	import("/Users/wware/CylindricalPrinter/software/models/Hollow_Dodecahedron.stl");
	for (i = [0:2])
		rotate(i * 144, [0,0,1])
			translate([0, 30, -H])
				intersection() {
					cylinder(h=H, r1=5, r2=1, $fn=6);
					cylinder(h=H, r=3, $fn=6);
				}
}

D = 110;

for (i = [0 : 1])
	for (j = [0 : 1])
		translate([(i-1/2) * D, (j-1/2) * D, 0]) {
			dodec();
}
