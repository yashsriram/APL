
void main()
{
  int *year;
  int *cntr;	

  *year = 1990; 
 
  if ( (*year/400)*400 == *year)		

	*cntr = 1;

  else if ( (*year/100)*100 == *year)

	*cntr = 2;

  else if ( (*year/4)*4 == *year )

	*cntr = 3;

  else
	*cntr = 4;
 
}
