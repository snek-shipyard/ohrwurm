# -*- coding: utf-8 -*-
import os
import io
import logging
import json

from django.conf import settings
from django.apps import AppConfig
from django.core.files import File

from telethon import TelegramClient, events, functions
from .file_handler import progress
import os
import time
import datetime
import asyncio
import threading

from pydub import AudioSegment

from asgiref.sync import sync_to_async

@sync_to_async
def _handel_incoming_audio(chat_id, chat_title, track_title, track_audio_file, chat_description=None, tags=None, attendees=None, transcript=None):
    from esite.track.models import Track, ProjectAudioChannel
    
    print("HANDLE AUDIO")
    def process_raw_data(obj_type: str, obj=None, for_streamfield=False):
        if isinstance(obj, dict):
            # obj = {
            #     camelcase_to_snake(k): process_raw_data(
            #         camelcase_to_snake(k), v
            #     )
            #     for (k, v) in obj.items()
            # }

            if for_streamfield:
                return [{"type": obj_type, "value": obj}]

        if isinstance(obj, list):
            """
            Get the singular of obj_type by removing s
            which is the last character
            """
            obj = [process_raw_data(obj_type[:-1], e) for e in obj]
            
            print(obj)

            if for_streamfield:
                return [{"type": obj_type[:-1], "value": obj}]

        return obj
    
    tags=process_raw_data(
                        "tags", tags, for_streamfield=True
                        )
    
    attendees = process_raw_data(
                            "attendees", attendees, for_streamfield=True
                         )
    print("a")
    tags = json.dumps(tags)
    print(tags)
    print("a")
    pac, created = ProjectAudioChannel.objects.update_or_create(channel_id=chat_id, defaults={"title": chat_title, "description": chat_description})
    track = Track.objects.create(pac=pac,
                         title=track_title,
                         description=chat_description,
                         audio_file=File(track_audio_file),
                         tags=tags,
                        #  attendees=json.dumps(attendees),
                         transcript=transcript
                         )
    
    print(track.__dict__)
    
    
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
            
            significances = "\n".join(["-" + i[0] for i in TagBlock.CHOICES])
            await event.respond(f"Usage: !custom tag name:significance\n{significances}")
            
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
            msg = await event.respond("Processing...")
            #> Check input file for audio mime type
            try:
                
                if event.message.file.mime_type in ["audio/mpeg3", "audio/x-mpeg3", "audio/x-wav"]:
                    start = time.time()
                    await msg.edit("**Downloading start...**")
                    audio_in = io.BytesIO()
                    audio_in = await client.download_media(event.message, audio_in, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, msg, start)))

                    #> Identify the specific audio format
                    if event.message.file.mime_type == 'audio/x-wav':
                        """Create autosegment from wav"""
                        audio_seg = AudioSegment.from_wav(audio_in)
                    elif event.message.file.mime_type == 'audio/x-mpeg3' or "audio/mpeg3":
                        """Create autosegment from mp3"""
                        #! Bug: Decoding failed. ffmpeg returned error code: 1
                        audio_seg = AudioSegment.from_mp3(audio_in)

                    #> Export audiosegment as ogg
                    audio_out = io.BytesIO()
                    audio_out = audio_seg.export(audio_out, bitrate="128k", format='ogg', codec="opus", parameters=["-strict", "-2", "-ac", "2", "-vol", "150"], tags={"ARTIST": "waveater", "GENRE": "Meeting/Trashtalk", "ALBUM": "waveater", "TITLE": f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}", "DATE": f"{event.message.media.document.date.strftime('%Y/%m/%d_%H:%M:%S')}", "COMMENT": f"A wav file converted to telegram voice message.", "CONTACT":"@waveater"})
                    audio_out.name = f"{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}.ogg"
                    
                    result = await client.send_file(event.chat_id, audio_out, voice_note=True, caption=f"{event.message.message}\n\n`track: '{event.message.file.name.split('.')[0]}_{event.message.media.document.date.strftime('%m-%d_%H-%M')}',\nchannel: '{audio_seg.channels}'',\nformat: 'ogg',\ncodec: 'opus',\nbitrate: '128k'`", reply_to=event.message)

                    await msg.delete()
                    
                    #> Get a more detailed chat message
                    try:
                        chat = await event.get_chat()
                        chat_detail = await client(functions.messages.GetFullChatRequest(
                            chat_id=chat.id
                        ))
                        chat_description = chat_detail.full_chat.about
                    except:
                        chat_description = None
                        
                        
                    #> Excract track information
                    track_name = event.message.file.name.split('.')[0]
                    attendees = [{"name": e} for e in event.message.text.split("@")[1:]]
                    tags = [{"name": e.split(":")[0], "significance": e.split(":")[1]} for e in event.message.text.split("!")[1:]]
                    
                    if hasattr(event._chat, "title"):
                        chat_title = event._chat.title
                    elif hasattr(event._chat, "username"):
                        chat_title = f"User: {event._chat.username}"
                        
                    await _handel_incoming_audio(chat_id=event._chat.id,
                                                chat_title=chat_title,
                                                chat_description=chat_description,
                                                track_title=track_name,
                                                track_audio_file=audio_out,
                                                tags=tags,
                                                attendees=attendees,
                                                )
            except Exception as e:
                print(e)
                await msg.edit(f"Shit happens! Something has gone wrong.\n\n**Error:** {e}")

        with client:
            client.run_until_disconnected()

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2020 miraculix-org Florian Kleber
