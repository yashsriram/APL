void main ()
{
	int a, b, c, d, e, f, g;
	int *p, *q, *r, *s, *t, *u, *v; 
     
        p=&a, q=&b, r=&c, s=&d, t=&e, u=&f, v=&g;
	*p = 13;
	*q = *p;
	*r = *q;
	*s = *r;
	*t = *s;
	*u = *t;
	*v = *u;
	*q = 13;
	*r = 13;
	*s = 13;
	*t = 13;
	*u = 13;
	*v = 13;

}

