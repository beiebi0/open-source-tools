BEGIN{FS=","}
{if($1!=lastState){
lastState=$1;
state++;}
}
END{print NR/state}
