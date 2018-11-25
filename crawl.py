import re, praw, requests, os, glob, sys, pygame
from bs4 import BeautifulSoup
from playsound import playsound

MIN_SCORE = 100

# if len(sys.argv) >= 2:
#     # the subreddit was specified:
#     SR_name = sys.argv[1]
#     targetSubreddit = sys.argv[1]
#     if len(sys.argv) >= 3:
#         # the desired minimum score was also specified:
#         MIN_SCORE = int(sys.argv[2])

imgurUrlPattern = re.compile(r'(https://i.imgur.com/(.*))(\?.*)?')

def downloadImage(imageUrl, localFileName, SR_name):
    try:
        P_name = SR_name + '/'
        if not os.path.exists(P_name):
            os.makedirs(P_name)
        response = requests.get(imageUrl)
        if response.status_code == 200:
            print('Downloading %s...' % (localFileName))
            with open(P_name + localFileName, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
    except:
        print('could not download %s' %imageUrl)

def reddit(sub, targetSubreddit):
    localF = re.search(r'/([\w.]+)$', sub.url)
    # print(localF.group(1))
    if localF:
        if len(glob.glob('%s/%s_%s_%s' % (targetSubreddit, targetSubreddit, sub.id, localF.group(1)))) > 0:
            print('skipped %s \nReason - already exists ' % sub.url)
        else:
            localFileName = '%s_%s_%s' % (targetSubreddit, sub.id, localF.group(1))
            downloadImage(sub.url, localFileName, targetSubreddit)

def imgur(sub, targetSubreddit):
    if '.jpg' in sub.url or '.png' in sub.url:
        p = re.search(r'(https://)(.*)', sub.url)
        imgurFilename = p.group(1) + 'i.' + p.group(2)
        localF = re.search(r'/([\w.]+)$', imgurFilename)
        if localF:
            # print(localF.group(1))
            if len(glob.glob('%s/%s_%s_%s' % (targetSubreddit, targetSubreddit, sub.id, localF.group(1)))) > 0:
                print('skipped %s \nReason - already exists ' % sub.url)
            else:
                localFileName = '%s_%s_%s' % (targetSubreddit, sub.id, localF.group(1))
                downloadImage(imgurFilename, localFileName, targetSubreddit)
    else:
        html = requests.get(sub.url).text
        soup = BeautifulSoup(html, 'html.parser')
        imageU = soup.find_all(href=re.compile('(jpg)?(png)?'),
                               class_=re.compile('(post-image-placeholder)?(zoom)?(shrinkToFit)?'))
        for string in imageU:
            url = re.search(r'href="([/.\w]+)', str(string))
            if url:
                imgurFilename = url.group(1)
                if '.jpg' in imgurFilename or '.png' in imgurFilename:
                    localF = re.search(r'/([\w.]+)$', imgurFilename)
                    if localF:
                        if len(glob.glob('%s/%s_%s_%s' % (
                        targetSubreddit, targetSubreddit, sub.id, localF.group(1)))) > 0:
                            print('skipped %s \nReason - already exists ' % sub.url)
                            continue
                        localFileName = '%s_%s_%s' % (targetSubreddit, sub.id, localF.group(1))
                        imgurFilename = 'https:' + imgurFilename
                        downloadImage(imgurFilename, localFileName, targetSubreddit)

def iimgur(sub, targetSubreddit):
    mo = imgurUrlPattern.search(
        sub.url)  # using regex here instead of BeautifulSoup because we are pasing a url, not html
    imgurFilename = mo.group(2)
    if '?' in imgurFilename:
        # The regex doesn't catch a "?" at the end of the filename, so we remove it here.
        imgurFilename = imgurFilename[:imgurFilename.find('?')]
    if len(glob.glob('%s/%s_%s_%s' % (targetSubreddit, targetSubreddit, sub.id, imgurFilename))) > 0:
        print('skipped %s \nReason - already exists ' % sub.url)
    else:
        localFileName = '%s_%s_%s' % (targetSubreddit, sub.id, imgurFilename)
        downloadImage(sub.url, localFileName, targetSubreddit)

def artstation(sub, targetSubreddit):
    localF = sub.url[sub.url.rfind('/') + 1:]
    if '?' in localF:
        localF = localF[:localF.find('?')]
    if len(localF) > 20:
        localF = localF[len(localF) - 20:]
    if len(glob.glob('%s/%s_%s_%s' % (targetSubreddit, targetSubreddit, sub.id, localF))) > 0:
        print('skipped %s \nReason - already exists ' % sub.url)
    else:
        localFileName = '%s_%s_%s' % (targetSubreddit, sub.id, localF)
        downloadImage(sub.url, localFileName, targetSubreddit)

def lostcause(sub, targetSubreddit):
    localF = sub.url[sub.url.rfind('/') + 1:]
    if '?' in localF:
        localF = localF[:localF.find('?')]
    if len(localF) > 20:
        localF = localF[len(localF) - 20:]
    print(localF)
    if len(glob.glob('%s/%s_%s_%s' % (targetSubreddit, targetSubreddit, sub.id, localF))) > 0:
        print('skipped %s \nReason - already exists ' % sub.url)
    else:
        localFileName = '%s_%s_%s' % (targetSubreddit, sub.id, localF)
        downloadImage(sub.url, localFileName, targetSubreddit)

def Iterate(submissions_hot, targetSubreddit):
    srno = 1
    for sub in submissions_hot:
        print('\n' + str(srno) + ' ' + sub.url)
        srno = srno + 1
        if sub.score < MIN_SCORE:
            print('skipped %s \nReason - min_score less.' % sub.url)
            continue

        if 'i.redd.it' in sub.url:
            reddit(sub, targetSubreddit)

        elif 'https://imgur.com/' in sub.url:
            try:
                imgur(sub, targetSubreddit)
            except:
                print('Could not download %s' % sub.url)
                continue

        elif 'https://i.imgur.com/' in sub.url:
            iimgur(sub, targetSubreddit)

        elif '.artstation.com' in sub.url and '.jpg' in sub.url or '.png' in sub.url or 'jpeg' in sub.url:
            artstation(sub, targetSubreddit)

        elif '.jpg' in sub.url or '.png' in sub.url or 'jpeg' in sub.url:
            lostcause(sub, targetSubreddit)

def main():
	if len(sys.argv) <= 1:
		print("Usage:- python crawl.py <subreddit list separated by spaces>")
    if len(sys.argv) >= 2:
    	subred = sys.argv[2:]
    print('Instantiating reddit object...')
    r = praw.Reddit('bot1', user_agent='Beauticap')
    for sub in subred:
        submissions_hot = r.subreddit(sub).hot(limit=25)
        # submissions_top = r.subreddit(targetSubreddit).top(limit=25, time_filter='day')
        Iterate(submissions_hot, sub)
    playsound('glass_ping.mp3')

if __name__ == '__main__':
    main()