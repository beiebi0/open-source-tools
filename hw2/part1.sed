1,/<table/d
/<\/table>/,$d
/<\/\{0,1\}tr>/d
/small-state-header/d
/^$/d
s/&nbsp;/ /g
s/<a href=[^>]*>//
s/<\/a>//
s/<[^>]*>//g
s/^[ \t]*//
s/[ \t]*$//
s/\([:digit:]*\)%/\1/g
