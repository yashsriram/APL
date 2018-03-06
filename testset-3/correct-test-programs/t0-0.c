void main()
{
	int a, b, *f,*g;

	f = &a;
        g = &b;
	
	if ((2 & *f)==2);
	*f=*g;
}
