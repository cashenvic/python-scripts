# original idea from https://github.com/larymak
import re
import os
from pytube import YouTube


def download_it(media_link):
    video = YouTube(str(media_link)).streams.first()
    video.download()
    print('🤴🏿✨️️ Completed like a boss! 😎️')
    print(f'You can find it here {os.getcwd()}/{video.default_filename}')


url = ''
while not re.search('(http|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?', url):
    url = input("Enter the youtube media url > ")

print(f'trying to media from download {url}')
download_it(url)
