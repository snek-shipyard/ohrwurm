import os

from django.core.exceptions import ValidationError


def validate_audio_file(value):
    if value._committed:
        return True

    file = value._file
    if file:
        if file.size > 12 * 1024 * 1024:
            raise ValidationError("Audio file too large ( > 12mb )")
        if not file.content_type in [
            "audio/mpeg",
            "audio/mp4",
            "audio/basic",
            "audio/x-midi",
            "audio/vorbis",
            "audio/x-pn-realaudio",
            "audio/vnd.rn-realaudio",
            "audio/x-pn-realaudio",
            "audio/vnd.rn-realaudio",
            "audio/wav",
            "audio/x-wav",
        ]:
            raise ValidationError(
                "Sorry, we do not support that audio MIME type. Please try uploading an mp3 file, or other common audio type."
            )
        if not os.path.splitext(file._name)[1] in [
            ".mp3",
            ".au",
            ".midi",
            ".ogg",
            ".ra",
            ".ram",
            ".wav",
        ]:
            raise ValidationError(
                "Sorry, your audio file doesn't have a proper extension."
            )
        return file
    else:
        raise ValidationError("Couldn't read uploaded file")
