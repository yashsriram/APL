
void main()
{
   int *n;
   int *cntr;	
   *n = 3;

 
   if ( *n & 1 == 0 )
      *cntr = 1;
   else 
      *cntr = 2;
 

   if ( (*n/2)*2 == *n )	
      *cntr = 3;
   else
      *cntr = 4;

}
