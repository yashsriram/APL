void main()
{
	int a, b, c;
	int *pa, *pb, *pc;
	pa = &a;
	pb = &b;
	pc = &c;
	*pa = 2;
	*pb = 4;

	*pc = *pa * *pb / -**pa;
}
