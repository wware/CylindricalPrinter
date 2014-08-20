#!/bin/sh

OPENSCAD=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD

$OPENSCAD simple.scad -o simple.stl
cat > foo.scad <<EOM
projection(cut=true)
    translate([0,0,-1.8])
        import("simple.stl");
EOM
$OPENSCAD foo.scad -o simple.dxf
rm -f simple.stl foo.scad
