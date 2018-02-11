void main()
{
   int d;
   int c;
   int b;
   int a;
   int *pa, *pb, *pc, *pd;

   *a = 5;
   *b = -a;
   *d = *a + 2;
   *c = *a + *b;
   *c = *a - *b;
   *c = *a * *b;
   *c = *a / *b;

}
