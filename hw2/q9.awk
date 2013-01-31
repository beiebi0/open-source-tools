BEGIN{FS=",";max=0;poll=""}
{tmp=$3-$5
if((tmp*tmp>max*max)&&($10!="Election 2006"))
	{if(tmp>0) max=tmp
	else max=tmp*(-1)
	poll=$10}
}
END{print poll,max}
