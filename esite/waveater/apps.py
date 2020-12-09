# -*- coding: utf-8 -*-
import os
import io
import logging

from django.conf import settings
from django.apps import AppConfig
from django.core.files import File

from .file_handler import progress
import os
import time
import datetime
import asyncio
import threading

from telethon import TelegramClient, events, functions
from pydub import AudioSegment
from asgiref.sync import sync_to_async

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@sync_to_async
def _handel_incoming_audio(chat_id, chat_title, audio_stream, chat_description=None):
    from esite.track.models import Track, ProjectAudioChannel
    
    print("HANDLE AUDIO")

    print(chat_id, chat_title, chat_description)
    pac, created = ProjectAudioChannel.objects.update_or_create(channel_id=chat_id, defaults={"title": chat_title, "description": chat_description})
    
    
    # ProjectAudioChannel

    return ProjectAudioChannel.objects.all()

class WaveaterConfig(AppConfig):
    name = 'esite.waveater'

    def ready(self):
        """Start the client."""
        print("waveaterbot started...")
        waveater_thread = threading.Thread(name="waveater-main-thread", target=Waveater.main)
        waveater_thread.daemon = False  # -> dies after main thread is closed
        waveater_thread.start()


class Waveater():
    def main():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = TelegramClient(None, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, loop=loop).start(bot_token=settings.TELEGRAM_BOT_TOKEN)

        @client.on(events.NewMessage(pattern='/start'))
        @client.on(events.NewMessage(pattern='/tags'))
        async def handle(event):
            from esite.track.blocks import TagBlock
            
            significances = " ".join([i[0] for i in TagBlock.CHOICES])
            await event.respond(f"Usage: !custom tag name:significance\nSignificances:{significances}")
        @client.on(events.NewMessage(pattern='/help'))
        async def start(event):
            print("test")
            """Send a message when the command /start is issued."""
            await event.respond("Hi..., I'm an audio slave! :3\nI would love to convert every wav you got into a telegram voice message. (>.<)")
            raise events.StopPropagation

        @client.on(events.NewMessage(pattern='/motivation'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond("OMG! Senpai, *o* let me convewt some wav into telegwam voice message, ~Nyaaaa")
            raise events.StopPropagation

        @client.on(events.NewMessage)
        async def handle(event):
            """Echo the user message."""
            # if telegram message has attached a wav file, download and convert it
            print(event.message.file.mime_type)
            if event.message.file:
                try:
                    chat = await event.get_chat()
                    chat_detail = await client(functions.messages.GetFullChatRequest(
                        chat_id=chat.id
                    ))
                except:
                    chat_detail = None
                
                try:
                    
                    if event.message.file.mime_type in ["audio/mpeg3", "auido/x-wav"]:
                        msg = await event.respond("Processing...")
                    
                        start = time.time()
                        await msg.edit("**Downloading start...**")
                        
                        audio_stream = io.BytesIO()
                        audio_stream = await client.download_media(event.message, audio_stream, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                            progress(d, t, msg, start)))
                        
                        if event.message.file.mime_type == "audio/x-wav":
                            audio_segment = AudioSegment.from_wav(audio_in)

                            audio_stream = io.BytesIO()
                            audio_stream = audio_segment.export(audio_stream, bitrate="128k", format='ogg', codec="opus", parameters=["-strict", "-2", "-ac", "2", "-vol", "150"], tags={"ARTIST": "waveater", "GENRE": "Meeting/Trashtalk", "ALBUM": "waveater", "TITLE": f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}", "DATE": f"{event.message.media.document.date.strftime('%Y/%m/%d_%H:%M:%S')}", "COMMENT": f"A wav file converted to telegram voice message.", "CONTACT":"@waveater"})
                            audio_stream.name = f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}.ogg"
                        
                        
                        print(event.message.text)
                        
                        tags = [{"name": e.split(":")[0], "significance": e.split(":")[1]} for e in event.message.text.split("!")[1:]]
                        print(tags)
                        
                        print(await _handel_incoming_audio(chat_id=event._chat.id, chat_title=event._chat.title, chat_description=chat_detail.full_chat.about, audio_stream=audio_stream, track_title="", track_audio_file="", audio_channel = "ffffffffff")
                        
                        # print(handel_incoming_tracks)
                        # pac = ProjectAudioChannel(
                        #     title = "models.CharField(null=True, blank=False, max_length=250)",
                        #     description = "models.TextField(null=True, blank=True)",
                        #     channel_id = "models.CharField(null=True, blank=False, max_length=250)",
                        #     avatar_image = models.ForeignKey(
                        #         settings.WAGTAILIMAGES_IMAGE_MODEL,
                        #         null=True,
                        #         blank=True,
                        #         related_name="+",
                        #         on_delete=models.SET_NULL,
                        #     )
                        # )
                        
                        # print(pac)
                        
                    
                except Exception as e:
                        print(e)
                        await msg.edit(f"OwO Shit happens! Something has gone wrong.\n\n**Error:** {e}")
            # if event.message.file and event.message.file.mime_type == 'audio/x-wav':
            #     msg = await event.respond("Processing...")

            #     try:
            #         start = time.time()

            #         await msg.edit("**Downloading start...**")

            #         audio_in = io.BytesIO()
            #         #audio_in.name = f"{event.message.file.name.split('.')[0]}_snek_{event.message.date.strftime('%m-%d_%H-%M')}.wav"
            #         audio_in = await client.download_media(event.message, audio_in, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            #             progress(d, t, msg, start)))
                    
            #         print(audio_in)

            #         audio_seg = AudioSegment.from_wav(audio_in)

            #         audio_out = io.BytesIO()
            #         audio_out = audio_seg.export(audio_out, bitrate="128k", format='ogg', codec="opus", parameters=["-strict", "-2", "-ac", "2", "-vol", "150"], tags={"ARTIST": "waveater", "GENRE": "Meeting/Trashtalk", "ALBUM": "waveater", "TITLE": f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}", "DATE": f"{event.message.media.document.date.strftime('%Y/%m/%d_%H:%M:%S')}", "COMMENT": f"A wav file converted to telegram voice message.", "CONTACT":"@waveater"})
            #         audio_out.name = f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}.ogg"
            #         #print(len(audio_seg)//1000)
            #         #print(event.message.file.id)
            #         #print(event.message.file.title)
            #         #print(event.message.file.performer)
            #         #print(event.message.file.name)
            #         #print(event.message.file.duration)
            #         from esite.track.models import Track, ProjectAudioChannel
            #         # pac = ProjectAudioChannel(
            #         #     title = "models.CharField(null=True, blank=False, max_length=250)",
            #         #     description = "models.TextField(null=True, blank=True)",
            #         #     channel_id = "models.CharField(null=True, blank=False, max_length=250)",
            #         #     # avatar_image = models.ForeignKey(
            #         #     #     settings.WAGTAILIMAGES_IMAGE_MODEL,
            #         #     #     null=True,
            #         #     #     blank=True,
            #         #     #     related_name="+",
            #         #     #     on_delete=models.SET_NULL,
            #         #     # )
            #         # )

            #         # track = TRACK(
            #         #     title = "dsssssssssssssdasdasadasdas",
            #         #     audio_channel = "ffffffffff",
            #         #     audio_format = "ffffffffff",
            #         #     audio_codec = "ffffffffff",
            #         #     audio_bitrate = "ffffffffff",
            #         #     description = "ffffffffff",
            #         #     transcript = "ffffffffff",
            #         #     pac = pac
            #         # )

            #         # track.audio_file.save("new_name.ogg", File(audio_out), True)

            #         result = await client.send_file(event.chat_id, audio_out, voice_note=True, caption=f"{event.message.message}\n\n`track: '{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}',\nchannel: '{audio_seg.channels}'',\nformat: 'ogg',\ncodec: 'opus',\nbitrate: '128k'`", reply_to=event.message)
            #         #print(result.file.duration)
            #         #print(result.file.performer)

            #         await msg.delete()

            #     except Exception as e:
            #         print(e)
            #         await msg.edit(f"OwO Shit happens! Something has gone wrong.\n\n**Error:** {e}")

        print(f"{threading.enumerate()}")
        with client:
            client.run_until_disconnected()

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2020 miraculix-org Florian Kleber
