
// Robotrola parametric reference CAD
// Units: millimeters. Reference geometry only.

$fn = 64;

module rounded_block(size=[60,40,20], r=4) {
  hull() {
    for (x=[-size[0]/2+r, size[0]/2-r])
    for (y=[-size[1]/2+r, size[1]/2-r])
    for (z=[-size[2]/2+r, size[2]/2-r])
      translate([x,y,z]) sphere(r=r);
  }
}

module servo_bracket(width=58, depth=42, height=42, wall=5) {
  cube([width, depth, wall], center=true);
  translate([-width/2+wall/2,0,height/2]) cube([wall, depth, height], center=true);
  translate([ width/2-wall/2,0,height/2]) cube([wall, depth, height], center=true);
}

module camera_bar(width=150) {
  rounded_block([width,24,28],3);
  translate([-55,0,24]) rounded_block([40,18,16],3);
  translate([ 55,0,24]) rounded_block([40,18,16],3);
}

module electronics_tray(w=210,d=125,h=55,wall=10) {
  cube([w,d,18], center=true);
  translate([-w/2+wall/2,0,h/2]) cube([wall,d,h], center=true);
  translate([ w/2-wall/2,0,h/2]) cube([wall,d,h], center=true);
  translate([0,-d/2+wall/2,h/2]) cube([w,wall,h], center=true);
  translate([0, d/2-wall/2,h/2]) cube([w,wall,h], center=true);
}

// Uncomment one part at a time before exporting from OpenSCAD.
// servo_bracket();
// camera_bar();
// electronics_tray();
