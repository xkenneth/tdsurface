from math import sin, cos, tan, acos, pi, radians

def min_curve_delta(d1, i1, a1, d2, i2, a2 ) :
    i1 = radians(i1)
    a1 = radians(a1)
    i2 = radians(i2)
    a2 = radians(a2)
    d1 = float(d1)
    d2 = float(d2)
    l = d2 - d1
    p = acos( ( cos(i1) * cos(i2) ) + ( sin(i1) * sin(i2) * cos(a2-a1) ) )    
    
    if p == 0 :
        print 'No Dog Leg!'
        v = l * cos(i2)
        n = l * sin(i2) * cos(a2)
        e = l * sin(i2) * cos(a2)
        return v,n,e
    
    
    
    v = tan(p/2) * l * (cos(i1) + cos(i2)) / p

    n = tan(p/2) * l * ( (sin(i1) * cos(a1)) + (sin(i2) * cos(a2)) ) / p

    e = tan(p/2) * l * ( (sin(i1) * sin(a1)) + (sin(i2) * sin(a2)) ) / p

    return v, n, e
