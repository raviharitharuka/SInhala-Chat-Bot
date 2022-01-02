import os
import sys
import argparse
import re
from urllib.request import Request, urlopen
from urllib.parse import quote
import urllib
import time
from collections import namedtuple
from playsound2 import playsound




def audio_extract(args=None,org_text=''):
    print(org_text)
    audio_args = namedtuple('audio_args',['language','output'])
    if args is None:
        args = audio_args(language='si-LK',output=open('output.mp3', 'w'))
    if type(args) is dict:
        args = audio_args(
                    language=args.get('language','si-LK'),
                    output=open(args.get('output','output.mp3'), 'w')
        )
    mp3url = f"https://translate.google.com.vn/translate_tts?ie=UTF-8&q="+quote(f"{org_text}")+"&tl=si&client=tw-ob" 
    headers = {"Host": "translate.google.com",
            "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
                            "AppleWebKit/535.19 (KHTML, like Gecko) "
                            "Chrome/18.0.1025.163 Safari/535.19"
    }
    req = Request(mp3url,headers=headers)
    sys.stdout.write('.')
    sys.stdout.flush() 
    response = urlopen(req)
    
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    with open('outputs/play.mp3','wb') as output:
        output.write(response.read())
    time.sleep(.5)

  
    playsound('outputs/play.mp3')


