
void main() {
  int *a, *b, *x, *y, *t, *gcd, *lcm;
  int  e, f, g, h, i, j, k, l;

  a = &e;
  b = &f;
  x = &h;
  y = &i;
  t = &j;
  gcd = &k;
  lcm = &l;

  
  *x = 14;
  *y = 36; 
 
  *a = *x;
  *b = *y;
 
  while (*b != 0  ) 
  {
   	*t = *b;
    	*b = (*a / *b) * *b;
    	*a = *t;
  }
 
  *gcd = *a;
  *lcm = (*x * *y) / *gcd;
 
  
}
