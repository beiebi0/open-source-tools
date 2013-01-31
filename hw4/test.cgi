#!/usr/bin/python

import cgi
import commands
import re

print "Content-type: text/html\n\n";
print '<html><head>'
print '<title>head2head</title>'
print '</head><body>'


form = cgi.FieldStorage()


if len(form.keys()) == 0 :

        rawlist = commands.getoutput("HEAD2HEAD_DATA=lt966 /home/lt966/Desktop/ost/assignment3/head2head item")
        categories = rawlist.split("\n")

        print '<p><b>Select category to vote:</b></p>'
        print '<form action="test.cgi" method="post" target="_self">'

        for category in categories:
                print '<input type="radio" name="category" id="%s" value="%s"/><label for="%s">%s</label><br>' %(category,category,category,category)

        print '<br><input type="submit" value="Select" />'
        print '</form>'

else :
        category = form.getvalue('category')
        if form.has_key('results'):
                category = form.getvalue('results')
                status , results = commands.getstatusoutput("HEAD2HEAD_DATA=lt966 /home/lt966/Desktop/ost/assignment3/head2head results '"+category+"'")
                if status == 0 :
                        print '<p><b> Results for %s :</b><br></p>' %category
                        print '<table border="1">'
                        print '<tr><td>Item name</td><td>Wins</td><td>Losses</td><td>Percent wins</td></tr>'
                        for result in results.split('\n') :
                                entries = result.split(',')
                                print '<tr>'
                                for entry in entries :
                                        print '<td>%s</td>' %entry
                                print '</tr>'
                        print '</table>'
                        print '<br><hr />'
                        print '<form name="test" action="test.cgi" method="post" target="_self">'
                        print '<input type="hidden" name="category" value="%s" /></form>' %category
                        print '<ul><li>Back to <a href="javascript:document.test.submit();">vote for %s </a></li>' %category
                        print '<li>Back to <a href="test.cgi"> categories</a></li></ul>'
                else :
                        print 'Error : No such category.<br>'
                        print 'Back to <a href="test.cgi"> categories</a>'
                exit()

        if  form.has_key('vote') and not form.has_key('skip'):
                f = open('/home/lt966/.head2head/lt966/'+category,'a')
                vote = form.getvalue('vote')
                f.write(vote+'\n')
                f.close()
                winning = form.getvalue('vote').split('/')[0]
                losing = form.getvalue('vote').split('/')[1]

                print '<em>You vote for "%s" over "%s".</em><br>' %(winning,losing)
                print '<p><b> Current totals:</b><br></p>'
                results = commands.getoutput("HEAD2HEAD_DATA=lt966 /home/lt966/Desktop/ost/assignment3/head2head results '"+category+"'")
                d = {}
                for result in results.split('\n') :
                        entry = result.split(',')
                        d[entry[0]] = entry[1]
                print '<table border="1"><tr><td>'+winning+'</td><td>'+d[winning]+'</td></tr>'
                print '<tr><td>'+losing+'</td><td>'+d[losing]+'</td></tr></table>'

                print '<hr />'


        print '<b>Category: </b>'+category

        items = commands.getoutput("HEAD2HEAD_DATA=lt966 /home/lt966/Desktop/ost/assignment3/head2head vote '"+category+"'")
        p = re.compile(r'\d\).*')
        item1 = p.findall(items)[0].replace('1) ','')
        item2 = p.findall(items)[1].replace('2) ','')

        print '<form action="test.cgi" method="post" target="_self">'
        print '<input type="radio" name="vote" id="%s" value="%s"/><label for="%s">%s</label><br>' %(item1,item1+'/'+item2,item1,item1)
        print '<input type="radio" name="vote" id="%s" value="%s"/><label for="%s">%s</label><br>' %(item2,item2+'/'+item1,item2,item2)
        print '<input type="hidden" name="category" value="%s"/>' %category
        print '<p><input type="submit" value="Vote!" /><input type="submit" name="skip" value="Skip"/></p></form>'


        print '<hr />'
        print '<ul><li>See <a href="?results=%s" >all results </a></li>' %category
        print '<li>Back to <a href="test.cgi"> categories</a></li></ul>'


print '</body></html>'

