BEGIN{FS=","}
{pollster=$10;
name[pollster]=pollster;
polls[pollster]++;
scores[pollster]+=$5}
END{
for(pollster in name){
avg= scores[name[pollster]]/polls[name[pollster]];
if(avg >max){ max = avg;
org = name[pollster];}
}
print org;
}
