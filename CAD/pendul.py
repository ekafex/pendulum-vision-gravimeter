from build123d import *
from math import cos, sin, radians

# -----------------------------
# Parameters (all in mm)
# -----------------------------

# Overall geometry
stand_height       = 180   # height of leg feet -> top plate bottom
top_plate_radius   = 55
top_plate_thickness = 6

# Legs
leg_height   = stand_height
leg_width    = 16
leg_depth    = 10
base_radius  = 75          # footprint radius (where legs roughly end)

# Camera + LED region
camera_platform_z   = 30   # bottom of camera platform above ground
camera_platform_thk = 6
camera_seat_size    = 40   # square pad for the cubic camera body
camera_seat_thk     = 4

# Clearance for lens / pendulum
lens_clear_radius   = 16   # central hole radius

# LED ring
led_ring_outer_r    = 55
led_ring_inner_r    = 35
led_ring_thickness  = 4
led_ring_z          = camera_platform_z + camera_platform_thk + 8

# Pivot at top
pivot_height        = 18
pivot_base_radius   = 10
pivot_tip_radius    = 2

# -----------------------------
# Helper: three-fold rotation
# -----------------------------

def three_fold_about_z(solid, radius):
    """
    Place 3 copies of 'solid' around Z axis at 0, 120, 240 degrees,
    centered at (radius, 0, 0) before rotation.
    The input solid is assumed centered at origin.
    """
    placed = None
    for i in range(3):
        angle = 120 * i
        # move along X, then rotate around Z
        s = Rot(0,0,angle)*Pos(radius, 0, 0)*solid
        placed = s if placed is None else placed + s
    return placed

# -----------------------------
# Legs
# -----------------------------

# Vertical box, bottom at z=0 when moved by leg_height/2
leg_template = Pos(0, 0, leg_height / 2)*Box(leg_width, leg_depth, leg_height)

# Radius where legs touch the floor (center of leg footprint)
leg_radius = base_radius - leg_width / 2

legs = three_fold_about_z(leg_template, leg_radius)

# -----------------------------
# Top triangular plate
# -----------------------------

# Create equilateral triangular plate, bottom at z = stand_height
top_plate_raw = extrude(RegularPolygon(top_plate_radius, 3), amount=top_plate_thickness)
top_plate = Pos(0, 0, stand_height)*top_plate_raw

# -----------------------------
# Camera platform and seat
# -----------------------------

# Circular platform
cam_platform_raw = Cylinder(base_radius, camera_platform_thk)
cam_platform = Pos(0, 0, camera_platform_z)*cam_platform_raw

# Square "seat" to help locate the camera body
camera_seat = Box(camera_seat_size, camera_seat_size, camera_seat_thk)
camera_seat = Pos(0, 0,camera_platform_z + camera_platform_thk + camera_seat_thk / 2)*camera_seat

# -----------------------------
# LED ring (as a thick washer)
# -----------------------------

outer_cyl = Cylinder(led_ring_outer_r, led_ring_thickness)
inner_cyl = Cylinder(led_ring_inner_r, led_ring_thickness)
led_ring_raw = outer_cyl - inner_cyl
led_ring = Pos(0, 0, led_ring_z)*led_ring_raw

# Because the ring radius overlaps with the legs, it will be
# mechanically supported where the solids intersect.

# -----------------------------
# Pivot / tripod top
# -----------------------------

pivot = Cone(pivot_base_radius, pivot_tip_radius, pivot_height)
pivot = Pos(0, 0, stand_height + top_plate_thickness)*pivot

# -----------------------------
# Central clearance (camera lens + pendulum path)
# -----------------------------

# A long cylinder that will be subtracted from the whole stand
clear_tube_height = stand_height + top_plate_thickness + pivot_height + 10
clear_tube = Pos(0, 0, 0)*Cylinder(lens_clear_radius, clear_tube_height)

# -----------------------------
# Combine everything
# -----------------------------

stand = legs + top_plate + cam_platform + camera_seat + led_ring + pivot
stand = stand - clear_tube  # central hole

# -----------------------------
# Export
# -----------------------------

# Export a single STL for printing
# export_stl(stand, "pendulum_stand_v1.stl")

# Optional: if you use ocp_vscode or CQ-editor style viewers, you can show it:
# from ocp_vscode import show
show_object(stand)





# show_object(r,options=dict(alpha=0.2))
# show_object(nut_hole, options=dict(alpha=0.3,color='red'))



