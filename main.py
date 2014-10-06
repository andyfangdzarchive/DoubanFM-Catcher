import requests
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC

DEFAULT_NUM = 360
chunk_size = 1000

def download(name, url):
  downloader = requests.get(url)
  with open(name, 'wb') as fd:
    for num, chunk in enumerate(downloader.iter_content(chunk_size)):
      fd.write(chunk)

def get_song(song):
  print("Downloading Music(%s)..." % song['title'])
  filename = song['sha256'] + '.mp3'
  download(filename, song['url'])

  print("Downloading meta-data...")
  download('tmp.jpg', song['picture'])
  audio = MP3(filename, ID3=ID3)
  try:
    audio.add_tags()
  except error:
    pass

  audio.tags.add(
    APIC(
      encoding=3, # 3 is for utf-8
      mime='image/jpeg', # image/jpeg or image/png
      type=3, # 3 is for the cover image
      desc=u'Cover',
      data=open('tmp.jpg', mode='rb').read()
    )
  )
  audio.tags.add(TIT2(encoding=3, text=song['title']))
  audio.tags.add(TALB(encoding=3, text=song['albumtitle']))
  audio.tags.add(TPE1(encoding=3, text=song['artist']))
  audio.tags.add(TDRC(encoding=3, text=song['public_time']))
  audio.save()

try:
  n = int(input('Target favourate songs number:'))
except:
  n = DEFAULT_NUM

payload_douban = {
  'app_name': 'radio_desktop_win',
  'version': '100',
  'user_id': '53915019',
  'expire': '1428150048',
  'token': 'c5cc8eb1ab',
  'channel': '-3',
  'type': 'n',
  'kbps': '192'
}
playlist = {}
while len(playlist) < n:
  try:
    r = requests.get('http://www.douban.com/j/app/radio/people', params=payload_douban)
    try:
      for song in r.json()['song']:
        playlist[song['sha256']] = song
      print("Got %d songs..." % len(playlist))
    except:
      print(r.json())
  except KeyboardInterrupt:
    break

for song in playlist:
  get_song(playlist[song])


