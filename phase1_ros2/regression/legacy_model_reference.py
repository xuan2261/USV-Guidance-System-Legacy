#!/usr/bin/env python3
"""Independent equation-level reference for the pinned legacy Viknes830 model.
This is a clean translation of the mathematical behavior, not copied source text.
"""
import math
M=3980.0; IZ=19703.0
X_U=-50.0; Y_V=-200.0; Y_R=0.0; N_V=0.0; N_R=-3224.0
X_UU=-135.0; Y_VV=-2000.0; N_RR=0.0; X_UUU=0.0; Y_VVV=0.0; N_RRR=-3224.0
FX_MIN=-6550.0; FX_MAX=13100.0; FY_MIN=-645.0; FY_MAX=645.0
RUDDER_D=4.0; KP_U=1.0; KP_PSI=5.0; KD_PSI=1.0
PI=math.pi

def ssa(a): return math.fmod(a+PI,2*PI)-PI

def normalize_angle_diff(angle, ref):
    if math.isinf(angle) or math.isinf(ref): return angle
    d=ref-angle
    out=angle+(d-math.fmod(d,2*PI)) if d>0 else angle+(d+math.fmod(-d,2*PI))
    d=ref-out
    if d>PI: out+=2*PI
    elif d<-PI: out-=2*PI
    return out

def deriv(s, cmd):
    x,y,raw_psi,u,v,r=s; u_d,psi_d=cmd
    psi=ssa(raw_psi); psi_d=normalize_angle_diff(psi_d,psi)
    c=math.cos(psi); q=math.sin(psi)
    cv0=(-M*v)*r; cv1=(M*u)*r; cv2=(M*v)*u+(-M*u)*v
    dv0=-(X_U+X_UU*abs(u)+X_UUU*u*u)*u
    dv1=-((Y_V*v+Y_R*r)+(Y_VV*abs(v)*v+Y_VVV*v**3))
    dv2=-((N_V*v+N_R*r)+(N_RR*abs(r)*r+N_RRR*r**3))
    fx=max(FX_MIN,min(FX_MAX,cv0+dv0+KP_U*M*(u_d-u)))
    fy=max(FY_MIN,min(FY_MAX,(KP_PSI*IZ*((psi_d-psi)-KD_PSI*r))/RUDDER_D))
    fn=RUDDER_D*fy
    return [c*u-q*v,q*u+c*v,r,(fx-cv0-dv0)/M,(fy-cv1-dv1)/M,(fn-cv2-dv2)/IZ]

def add(s,k,h): return [a+h*b for a,b in zip(s,k)]
def step(s,cmd,dt):
    k1=deriv(s,cmd); k2=deriv(add(s,k1,dt/2),cmd); k3=deriv(add(s,k2,dt/2),cmd); k4=deriv(add(s,k3,dt),cmd)
    k=[(a+2*b+2*c+d)/6 for a,b,c,d in zip(k1,k2,k3,k4)]
    return add(s,k,dt)
def trajectory(state,cmd,duration,dt):
    out=[(0.0,list(state))]; s=list(state); n=round(duration/dt)
    for i in range(n): s=step(s,cmd,dt); out.append(((i+1)*dt,list(s)))
    return out
