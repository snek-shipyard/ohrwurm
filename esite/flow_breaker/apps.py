from django.apps import AppConfig
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
from telegram.utils.request import Request
from django.conf import settings
from pydub import AudioSegment
import os


class FlowBreakerConfig(AppConfig):
    name = 'esite.flow_breaker'



# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2020 miraculix-org Florian Kleber
