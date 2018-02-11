void main()
{
   int z;
   int y;
   int x;
   int *px, *py, *pz;

   *px = 5;
   *y = 1;
   *pz = 1;
   *z = **px + *py - ***px;
   sdasz = -z * &y + *x;

}
