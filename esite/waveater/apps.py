# -*- coding: utf-8 -*-
import os
import io
import logging

from django.conf import settings
from django.apps import AppConfig

from telethon import TelegramClient, events
from .file_handler import progress
import os
import time
import datetime
import asyncio
import threading

from pydub import AudioSegment


class WaveaterConfig(AppConfig):
    name = 'esite.flow_breaker'

    def ready(self):
        """Start the client."""
        print("waveaterbot started...")
        waveater_thread = threading.Thread(name="waveater-main-thread", target=Waveater.main)
        waveater_thread.daemon = False  # -> dies after main thread is closed
        waveater_thread.start()


class Waveater():
    def main():
        loop = asyncio.new_event_loop()
        client = TelegramClient('anon', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, loop=loop).start(bot_token=settings.TELEGRAM_BOT_TOKEN)
        
        @client.on(events.NewMessage(pattern='/start'))
        @client.on(events.NewMessage(pattern='/help'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond("Hi, I'm an audio slave! :3\nI would love to convert every wav you got into a telegram voice message. (>.<)")
            raise events.StopPropagation

        @client.on(events.NewMessage(pattern='/motivation'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond("OMG! Senpai, *o* let me convewt some wav into telegwam voice message, ~Nyaaaa")
            raise events.StopPropagation

        @client.on(events.NewMessage)
        async def echo(event):
            """Echo the user message."""
            # if telegram message has attached a wav file, download and convert it
            if event.message.file and event.message.file.mime_type == 'audio/x-wav':
                msg = await event.respond("Processing...")
                
                try:    
                    start = time.time()
                    
                    await msg.edit("**Downloading start...**")

                    audio_in = io.BytesIO()
                    #audio_in.name = f"{event.message.file.name.split('.')[0]}_snek_{event.message.date.strftime('%m-%d_%H-%M')}.wav"
                    audio_in = await client.download_media(event.message, audio_in, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, msg, start)))

                    audio_seg = AudioSegment.from_wav(audio_in)

                    audio_out = io.BytesIO()
                    audio_out = audio_seg.export(audio_out, bitrate="128k", format='ogg', codec="opus", parameters=["-strict", "-2", "-ac", "2", "-vol", "150"], tags={"ARTIST": "waveater", "GENRE": "Meeting/Trashtalk", "ALBUM": "waveater", "TITLE": f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}", "DATE": f"{event.message.media.document.date.strftime('%Y/%m/%d_%H:%M:%S')}", "COMMENT": f"A wav file converted to telegram voice message.", "CONTACT":"@waveater"})
                    audio_out.name = f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}.ogg"
                    #print(len(audio_seg)//1000)
                    #print(event.message.file.id)
                    #print(event.message.file.title)
                    #print(event.message.file.performer)
                    #print(event.message.file.name)
                    #print(event.message.file.duration)
                    result = await client.send_file(event.chat_id, audio_out, voice_note=True, caption=f"{event.message.message}\n\n`track: '{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}',\nchannel: '{audio_seg.channels}'',\nformat: 'ogg',\ncodec: 'opus',\nbitrate: '128k'`", reply_to=event.message)
                    #print(result.file.duration)
                    #print(result.file.performer)

                    await msg.delete()

                except Exception as e:
                    print(e)
                    await msg.edit(f"OwO Shit happens! Something has gone wrong.\n\n**Error:** {e}")

        #print(f"{threading.enumerate()}")
        with client:
            client.run_until_disconnected()

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2020 miraculix-org Florian Kleber
