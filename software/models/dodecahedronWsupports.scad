// dimensions are in millimeters, half-inch-high supports
H = 12.7;

module support(x, y, H) {
    widest = 5;
    dmin = 0.7;
    gap = 1;
    n = 6;
    translate([x, y, 0]) {
        cylinder(d1=10, d2=dmin, h=H-gap+0.01, $fn=n);
        translate([0, 0, H-gap])
            cylinder(d=dmin, h=gap+0.01, $fn=n);
    }
}

module dodec() {
	import("/Users/wware/CylindricalPrinter/software/models/Hollow_Dodecahedron.stl");
	for (i = [0:2])
		rotate(i * 144, [0,0,1])
			translate([0, 30, -H])
				support(0, 0, H);
}

dodec();
