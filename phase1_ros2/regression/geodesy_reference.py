#!/usr/bin/env python3
import json,math,sys
from pathlib import Path
A=6378137.0; F=1.0/298.257223563; E2=F*(2.0-F)
def ecef(lat_deg,lon_deg,h):
    lat=math.radians(lat_deg); lon=math.radians(lon_deg); s=math.sin(lat); c=math.cos(lat)
    n=A/math.sqrt(1.0-E2*s*s)
    return ((n+h)*c*math.cos(lon),(n+h)*c*math.sin(lon),(n*(1.0-E2)+h)*s)
def enu(origin,point):
    x0,y0,z0=ecef(*origin); x,y,z=ecef(*point); dx,dy,dz=x-x0,y-y0,z-z0
    lat=math.radians(origin[0]); lon=math.radians(origin[1]); sl,cl=math.sin(lon),math.cos(lon); sp,cp=math.sin(lat),math.cos(lat)
    return (-sl*dx+cl*dy, -sp*cl*dx-sp*sl*dy+cp*dz, cp*cl*dx+cp*sl*dy+sp*dz)
def main():
    p=Path(__file__).with_name('geodesy_fixtures.json'); d=json.loads(p.read_text()); o=d['origin']; origin=(o['latitude_deg'],o['longitude_deg'],o['altitude_m']); tol=d['tolerance_m']; ok=True; rows=[]
    for f in d['fixtures']:
        got=enu(origin,tuple(f['geo'])); err=max(abs(a-b) for a,b in zip(got,f['enu_m'])); passed=err<=tol; ok&=passed; rows.append({'id':f['id'],'pass':passed,'max_error_m':err,'computed_enu_m':got})
    out={'status':'PASS' if ok else 'FAIL','fixtures':rows}; print(json.dumps(out,indent=2)); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
