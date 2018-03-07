void main()
{
   int a, b, *i1,*f1;
 
   i1 = &a;
   f1 = &b;

   *i1 = 3;
   *f1 = 2;

   if(*f1 < 5 != 0)
   {
      *i1 = *i1 + *i1;
      *f1 = *f1 + 1;
   }
}
