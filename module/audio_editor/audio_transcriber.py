import datetime
import logging
import os
import time
import opencc
import srt
import torch
import whisper
from tqdm import tqdm
from . import (
    utils,
)


class AudioTranscriber:
    def __init__(self, directory, output_path):
        self.directory = directory
        self.output_path = output_path

    def export(self):
        return None
