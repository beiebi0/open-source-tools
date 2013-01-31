BEGIN{FS=",";max=0;maxState=""}
{
if($1!=state){
if(polls>max){
maxState=state;
max=polls;
}
state=$1;
polls=0;
}
polls++;
}
END{if(polls>max){maxState=state;max=polls;}
print maxState}
