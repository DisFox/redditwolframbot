import urllib, requests, time, praw, xml.etree.ElementTree as ET, os, re

def redditescape(string):
        escape = '\\`*_{}[]()#+-.!^'
        for char in escape:
                string = string.replace(char, '\\' + char)
        return string

def getdata(mathstring,appid):
        url = 'http://api.wolframalpha.com/v2/query?input=' + urllib.quote(mathstring) + '&appid=' + appid + '&format=plaintext'
        r = requests.get(url)
        return r.text.encode('utf8')
        
def getimportant(xml):
        important = {}
        blacklist = ['PropertiesAsARealFunction']
        root = ET.fromstring(xml)
        for child in root.iter('pod'):
                try:
                        title = child.attrib['title']
                        pid = child.attrib['id']
                        if pid not in blacklist:
                                images = []
                                for subpod in child.findall('subpod'):
                                        for image in subpod.findall('img'):
                                                ititle = image.attrib['title']
                                                if ititle == '':
                                                        ititle = title
                                                images.append('[' + redditescape(ititle) + '](' + image.attrib['src'] + '.gif)')
                                if images != []:
                                        important[title] = '\r\n\r\n'.join(images).encode('utf8')
                except TypeError:
                        pass
        return important

def main():
        if os.path.exists("wolframids.txt") != True:
                with open("wolframids.txt",'w') as w:
                        alreadyposted = []                        #Creates database if it doesn't exist, reads if it does
        else:
                with open("wolframids.txt","a+") as w:
                        alreadyposted = w.read().splitlines()
                        
        appid = '' # Your Wolfram Alpha appid
        r = praw.Reddit(user_agent='Wolfram Alpha Bot') # Useragent
        r.login('','') # Reddit username and password
        subreddit = '' #This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
        while True:
                for comment in praw.helpers.comment_stream(r,subreddit,limit = None, verbosity=0):#in comments:
                        commentid = comment.id
                        if commentid not in alreadyposted:
                                body = comment.body.lower()
                                if body.find('@wolfram_bot[') != -1:
                                        try:
                                                print 'Found Comment: ' + str(commentid)
                                                regex = re.compile(r'@wolfram_bot\[.*\]')
                                                findall = regex.findall(body.encode('utf8'))
                                                redditinput = findall[0]
                                                redditinput = redditinput[13:-1]
                                                data = getimportant(getdata(redditinput,appid))
                                                rcomment = []
                                                for d in data:
                                                        rcomment.append('**' + d + ':' + '**')
                                                        rcomment.append(data[d])
                                                rcomment =  '\r\n\r\n'.join(rcomment)
                                                try:
                                                        comment.reply(rcomment)
                                                except:
                                                        comment.reply('Invalid Query')
                                                print 'Replied to ' + commentid
                                                with open("wolframids.txt","a+") as w:
                                                        w.write(commentid + '\n')
                                                        alreadyposted.append(commentid)
                                        except Exception as e:
                                                print 'Error: ' + str(e)
                print 'done'
                time.sleep(10)

if __name__ == '__main__':
        main()
