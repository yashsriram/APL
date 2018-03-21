int *g3, l3;
int *func1(int *x, int *y);
int *func2(int *a, float *b);
float *var1, var2;
int *func1(int *a, int *b)
{
    int **h;
    *g3 = 4;
    return g3;
}

int *func2(int *b1, float *b2)
{
    int *h1;
    if(*b1 == 32)
    {
        *var1 = 3.0;
    }
    else
    {
        while(*b2 != *var1)
        {

            *b2 = *b2 - 1.0;
        }
    } 
    return h1;
}
void main()
{
    int *g, **a1, *a2, a;
    float **f;
    *g = 4;
    if(*g == 4)
    {
        while(*g != 0)
        {
            *g = *g - 1;
        }
        **f = 3.0;
    }
    else
    {
        **f = 2.0;
    }   
    *g = func1(*g3, *a2);
}
