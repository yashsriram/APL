void main ()
{
	int a, b, c;
	int *p, *q, *r;
        
        p=&a, q=&b, r=&c;
	*q = 4, *r = 3;
	*p = *q;
	*p = *r;
	*q = *p;
}
