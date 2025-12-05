from build123d import *
import math

Rt,ht,Rft=60,10,10
cr1,cr2,chh,cw = 8,1,3,2
ll,lxy,lw,lfw,lww=180,15,5,5,4
ang_open_legs = 20
cosA,sinA = math.cos(math.radians(ang_open_legs)),math.sin(math.radians(ang_open_legs))
cosT,sinT = math.cos(math.radians(210)),math.sin(math.radians(210))
RRR = Rt-Rft-lxy-5
leg2top = 2

top = RegularPolygon(radius=Rt, side_count=3)
top = fillet(top.vertices(),Rft)
top = extrude(top, ht)
top += Pos(0,0,(ht-chh)/2)*Rot(180,0,0)*Cone(cr1+cw,cr2+cw,ht+chh) 
top -= Pos(0,0,(ht-chh)/2)*Rot(180,0,0)*Cone(cr1,cr2,ht+chh)

# top = fillet(top.edges().sort_by(Axis.Z)[4:],2)
# top = fillet(top.edges().sort_by(Axis.Z)[:2],0.5)

##################################

body_leg = Rectangle(lxy,lxy)-Rectangle(lxy-lw,lxy-lw)
body_leg = fillet(body_leg.vertices(),5)
body_leg = Rot(0,-ang_open_legs,0)*extrude(body_leg,-ll)
body_leg -= extrude(Rectangle(1.5*lxy,1.5*lxy), lxy*sinA)
body_leg -= Pos(ll*sinA,0,-ll*cosA)*Box(1.5*lxy,1.5*lxy, lxy*sinA)

leg_top = Pos(-1.5,0,0)*extrude(Rectangle(lxy+lww,lxy+lww),-(lxy+2)/2*sinA)
leg_bot = Pos(ll*sinA-1.,0,-ll*cosA+lww)*Box(lxy+lww,lxy+lww, lww)

top -= Pos(RRR,0,leg2top)*leg_top+Pos(RRR*sinT,-RRR*cosT,leg2top)*Rot(0,0,120)*leg_top+Pos(RRR*sinT,RRR*cosT,leg2top)*Rot(0,0,-120)*leg_top

#################################
# # fillet part
# leg_top = fillet(leg_top.edges().sort_by(Axis.Z)[:8],1)
# leg_bot = fillet(leg_bot.edges().sort_by(Axis.Z)[4:8],4)
# leg_bot = fillet(leg_bot.edges(),1)
#################################

leg_full = body_leg+leg_top+leg_bot
legs  = Pos(RRR, 0,leg2top)*leg_full
legs += Pos(RRR*sinT,-RRR*cosT,leg2top)*Rot(0,0,120)*leg_full + Pos(RRR*sinT,RRR*cosT,leg2top)*Rot(0,0,-120)*leg_full

#####################################




show_object(top,options=dict(alpha=0.0))
show_object(legs,options=dict(alpha=0.,color="red"))
# show_object(rr,options=dict(alpha=0.0))
# show_object(rr2,options=dict(alpha=0.6,color="red"))
# show_object(rr3,options=dict(alpha=0.6,color="red"))
