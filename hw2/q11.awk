BEGIN{FS=","}
{polls[$10]++;}
END{for(name in polls) print name,polls[name]}
