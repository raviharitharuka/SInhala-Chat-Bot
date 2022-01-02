from __future__ import division
import time
from google.cloud import speech
from Speech import Microphone
from Speech import speech_to_text
from Translate import translate
from Audio import playx
import sys
import json
import random

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


'''
    Start Listing
    if User Said Ayubowan
        stop lisiting
        Say Back Ayubowan
        then start loop
            say q
            lisiting a wait 1 minute
            if voice captured
                if a is correct
                    say reward
                else
                    say reward
                    say correct answer if there is, other wise contiure
            else
                say do you want go next quecstion
    else
        wait
'''


def startLisiting():
    streaming_config, client = speech_to_text.configure()
    with Microphone.MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)
        final_text = speech_to_text.listen_print_loop(responses)
        translated_text = translate.fetch_translation(final_text)
        return translated_text, final_text


def StartBot(text='', org_text=''):
    is_started = True
    text = text.strip()
    org_text = org_text.strip()
    if text == "Welcome" or text == "Hi":
        is_started = False
        print("bot detected")
        playx.audio_extract(org_text=org_text)
    return is_started, True


def loadIntetns():
    data = []
    with open('bot_intents/intents.json', encoding="utf-8") as f:
        data = json.load(f)
    intetns_list = data.get('intents')
    return intetns_list


def loopIntents(intetns_list=[]):
    if len(intetns_list):
        for inetent in intetns_list:
            qecstion = inetent.get('qecstion')
            answer = inetent.get('answer')
            reply = inetent.get('reply')
            reply_negative_q = inetent.get('reply_negative_q')
            reply_negative_a_reply = inetent.get('reply_negative_a_reply')

            playx.audio_extract(org_text=qecstion)
            translated_text, org_text = startLisiting()
            time.sleep(random.randint(0, 3))
            if not len(answer):
                if not checkPositivity():
                    playx.audio_extract(org_text='say something positive')
                else:
                    playx.audio_extract(org_text='say something positive')

                playx.audio_extract(org_text=reply)
            else:
                if checkAnswerIsCorrect(answer=translated_text):
                    playx.audio_extract(org_text=reply)
                else:
                    playx.audio_extract(org_text=reply_negative_q)
                    translated_text_, org_text_ = startLisiting()
                    playx.audio_extract(org_text=reply_negative_a_reply)


def checkAnswerIsCorrect(answer=''):
    translated_text = translate.fetch_translation(answer)


def main():
    is_listing = True
    is_began_loop = False
    while(is_listing):
        translated_text, org_text = startLisiting()
        is_listing, is_began_loop = StartBot(translated_text, org_text)
    if is_began_loop:
        intetns_list = loadIntetns()
        random.shuffle(intetns_list)
        loopIntents(intetns_list)


if __name__ == "__main__":
    main()
