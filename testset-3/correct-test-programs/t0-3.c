void main()
{
	int *a,*b, e, f;
   
        a = &e;
        b = &f;

	if (*a >= - *b)
		*a = *a+1;
	else
		*b = *b+1;
}
