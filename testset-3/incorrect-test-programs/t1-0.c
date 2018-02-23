
void main() {
  int *a, *b, *x, *y, *t, *gcd, *lcm;
  
  *x = 14;
  *y = 36; 
 
  *a = *x;
  *b = *y;
 
  while (*b != 0  ) 
  {
   	*t = *b;
    	*b = (*a / ****b) * *b;
    	*a = *t;
  }
 
  *gcd = *a;
  *lcm = (*x * *y) / *gcd;
 
  
}
