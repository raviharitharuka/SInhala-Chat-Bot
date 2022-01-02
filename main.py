from __future__ import division
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from google.cloud import speech
from kivy.core.text import Text
from Speech import Microphone
from Speech import speech_to_text
from Translate import translate
from Audio import playx
import time
import sys
import json
import random
from tkinter import *
import threading
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
nltk.download('vader_lexicon')

# from chat import get_response, bot_name

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class ChatApplication:

    def __init__(self):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("Ai Agent")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        # head label
        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)

        # tiny divider
        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        # text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                                font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)

        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)

        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50",
                               fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06,
                             rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        # send button
        send_button = Button(bottom_label, text="Bot", font=FONT_BOLD, width=20, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        self.thread = threading.Thread(target=self.startLoop)
        self.thread.start()

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        # self.msg_entry

    def startLoop(self):
        is_listing = True
        is_began_loop = False
        while(is_listing):
            translated_text, org_text = self.startLisiting()
            is_listing, is_began_loop = self.StartBot(
                translated_text, org_text)
        if is_began_loop:
            intetns_list = self.loadIntetns()
            # random.shuffle(intetns_list)
            self.loopIntents(intetns_list)

    def startLisiting(self):
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

    def get_cosine_sim(self, strs=[]):
        vectors = [t for t in self.get_vectors(strs)]
        similarityes = cosine_similarity(vectors)
        return [np.round(item, 3) for item in list(similarityes.flatten())][1]

    def get_vectors(self, strs=[]):
        text = [t for t in strs]
        vectorizer = CountVectorizer(text)
        vectorizer.fit(text)
        arrays = vectorizer.transform(text).toarray()
        return arrays

    def getSentiment(self, text):
        sid = SentimentIntensityAnalyzer()
        sid.polarity_scores(f'{text}')
        sid = SentimentIntensityAnalyzer()
        neu = sid.polarity_scores('happy').get('neu')
        pos = sid.polarity_scores('happy').get('pos')
        return neu, pos

    def StartBot(self, text='', org_text=''):
        is_started = True
        text = text.strip()
        org_text = org_text.strip()
        self._insert_message(org_text, "You >")
        time.sleep(random.randint(0, 2))
        if text == "Welcome" or text == "Hi":
            is_started = False
            self._insert_message(org_text, "Bot >")
            print("bot detected")
            playx.audio_extract(org_text=org_text)
        return is_started, True

    def loadIntetns(self):
        data = []
        with open('bot_intents/intents.json', encoding="utf-8") as f:
            data = json.load(f)
        intetns_list = data.get('intents')
        return intetns_list

    def loopIntents(self, intetns_list=[]):
        if len(intetns_list):
            for inetent in intetns_list:
                qecstion = inetent.get('qecstion')
                answer = inetent.get('answer')
                reply = inetent.get('reply')
                reply_negative_q = inetent.get('reply_negative_q')
                reply_negative_a_reply = inetent.get('reply_negative_a_reply')
                self._insert_message(qecstion, "You >")
                playx.audio_extract(org_text=qecstion)
                translated_text, org_text = self.startLisiting()
                self._insert_message(org_text, "You >")
                if not len(answer):
                    self._insert_message(reply, "Bot >")
                    playx.audio_extract(org_text=reply)
                else:
                    if self.checkAnswerIsCorrect(answer=translated_text, organswr=answer):
                        self._insert_message(reply, "Bot >")
                        playx.audio_extract(org_text=reply)
                    else:
                        self._insert_message(reply_negative_q, "Bot >")
                        playx.audio_extract(org_text=reply_negative_q)
                        translated_text_, org_text_ = self.startLisiting()
                        self._insert_message(org_text_, "You >")
                        nue, pos = self.getSentiment(translated_text_)
                        if pos > 0.0:
                            self._insert_message(
                                reply_negative_a_reply, "Bot >")
                            playx.audio_extract(
                                org_text=reply_negative_a_reply)
                        else:
                            pass
                            self._insert_message(
                                reply_negative_a_reply, "Bot >")
                            playx.audio_extract(
                                org_text=reply_negative_a_reply)
            if self.thread.is_alive:
                self.thread.join()

    def checkAnswerIsCorrect(self, answer='', organswr=''):
        translated_text = translate.fetch_translation(answer)
        print(f'answer {answer}')
        try:
            score = self.get_cosine_sim([organswr, translated_text])
            print(f'score {score}')
            if score > 0.5:
                return True
            else:
                return False
        except:
            ix = organswr.split(' ')
            ix2 = translated_text.split(' ')

            if ix == ix2:
                return True
            else:
                return False

    def checkPositivity():
        return True

    def _insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)

        msg2 = f" no: no\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.configure(state=DISABLED)

        self.text_widget.see(END)


if __name__ == "__main__":
    app = ChatApplication()
    app.run()
