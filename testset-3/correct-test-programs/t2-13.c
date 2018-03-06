void main(){
	int l,t,a,m,n,b,u,v;
	int *pl,*pt,*pa,*pm,*pn,*pb,*pu,*pv;
	pl=&l;
	pt=&t;
	pa=&a;
	pm=&m;
	pn=&n;
	pb=&b;
	pu=&u;
	pv=&v;
	if(*pl<2){
	*pa=20;
	if(*pb<4){
		*pa=40;
	}
	else if(*pm<30){
		*pt=0;
	}
	else if(*pu<30){
		*pv=0;
	}
	else{
		*pb=0;
	}
	*pu=90;
	}
	else{
		
	*pu=20;
	if(*pb<4){
		*pv=40;
	}
	else if(*pm<30){
		*pm=0;
	}
	else if(*pu<30){
		*pn=0;
	}
	else{
		*pt=0;
	}
	*pu=90;
	}
}
