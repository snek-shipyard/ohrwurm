# myapp/_init_.py
import os

if os.environ.get('RUN_MAIN', None) != 'true':
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    default_app_config = 'esite.waveater.apps.WaveaterConfig'
    
# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2020 miraculix-org Florian Kleber
