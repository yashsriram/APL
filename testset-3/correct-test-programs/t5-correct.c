
void main()
{
   int a, b, *n, *cntr;	

   n = &a;
   cntr = &b;

   *n = 3;

 
   if ( *n> 5 || 1 == 0 )
      *cntr = 1;
   else 
      *cntr = 2;
 

   if ( (*n/2)*2 == *n )	
      *cntr = 3;
   else
      *cntr = 4;

}
