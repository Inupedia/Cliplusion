import os
import srt
import whisper
from pydub import AudioSegment
import opencc
import time
import torch
from . import utils
import logging
from datetime import timedelta
from pysubs2 import SSAFile, SSAEvent


class AudioTranscriber:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.vad_model = None  # Initialize attribute
        self.detect_speech = None  # Initialize attribute
        self.sampling_rate = 16000
        self.whisper_model = None
        self.language = "en"
        self.initial_prompt = "Please say something into the microphone."
        self.audio_files = [
            os.path.join(input_directory, f)
            for f in os.listdir(input_directory)
            if f.endswith((".wav", ".mp3", ".m4a"))
        ]

    def _detect_voice_activity(self, audio):
        """Detect segments that have voice activities"""
        tic = time.time()
        if self.vad_model is None or self.detect_speech is None:
            # torch load limit https://github.com/pytorch/vision/issues/4156
            torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
            self.vad_model, funcs = torch.hub.load(
                repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True
            )

            self.detect_speech = funcs[0]

        # Correcting here: Removing the 'num_steps' or any other unwanted arguments
        speeches = self.detect_speech(
            audio, self.vad_model, sampling_rate=self.sampling_rate
        )

        # Remove too short segments
        speeches = utils.remove_short_segments(speeches, 1.0 * self.sampling_rate)

        # Expand to avoid to tight cut. You can tune the pad length
        speeches = utils.expand_segments(
            speeches, 0.2 * self.sampling_rate, 0.0 * self.sampling_rate, audio.shape[0]
        )

        # Merge very closed segments
        speeches = utils.merge_adjacent_segments(speeches, 0.5 * self.sampling_rate)

        logging.info(f"Done voice activity detection in {time.time() - tic:.1f} sec")
        return speeches if len(speeches) > 1 else [{"start": 0, "end": len(audio)}]

    def _transcribe(self, audio, speech_timestamps):
        """Transcribe the detected speech segments in the audio."""

        if self.whisper_model is None:
            # Assuming you have a method or utility to load the Whisper model
            self.whisper_model = whisper.load_model("base.en", device="cpu")

        transcriptions = []

        for seg in speech_timestamps:
            segment_audio = audio[int(seg["start"]) : int(seg["end"])]
            # Obtain the transcription result for the audio segment
            result = self.whisper_model.transcribe(
                segment_audio,
                task="transcribe",
                # 'language' and 'initial_prompt' are assumed to be attributes or passed arguments
                language=self.language,
                initial_prompt=self.initial_prompt,
            )
            result["origin_timestamp"] = seg
            transcriptions.append(result)

        return transcriptions

    def _save_srt(self, transcribe_results, audio_filename):
        subs = SSAFile()

        def _add_sub(start, end, text):
            subs.append(
                SSAEvent(
                    start=datetime.timedelta(seconds=start),
                    end=datetime.timedelta(seconds=end),
                    text=text,
                )
            )

        for s in transcribe_results:
            _add_sub(s["start"], s["end"], s["text"])

        base_audio_name = os.path.splitext(audio_filename)[0]
        output_file = os.path.join(self.output_path, f"{base_audio_name}.srt")

        # Ensure the directory exists
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(subs.to_string(format="srt"))

    def _save_md(self, transcribe_results, audio_filename):
        base_audio_name = os.path.splitext(audio_filename)[0]
        output_file = os.path.join(self.output_path, f"{base_audio_name}.md")

        # Ensure the directory exists
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        with open(output_file, "w", encoding="utf-8") as f:
            for s in transcribe_results:
                f.write(f"### {s['start']} - {s['end']}\n")
                f.write(f"{s['text']}\n\n")

    def transcribe_all(self):
        for input_file in self.audio_files:
            audio = whisper.load_audio(input_file, sr=self.sampling_rate)
            speech_timestamps = self._detect_voice_activity(audio)
            transcribe_results = self._transcribe(audio, speech_timestamps)

            base_name = os.path.basename(input_file)
            name, _ = os.path.splitext(base_name)

            # Save SRT and Markdown
            self._save_srt(
                os.path.join(self.output_directory, f"{name}.srt"), transcribe_results
            )
            self._save_md(
                os.path.join(self.output_directory, f"{name}.md"), transcribe_results
            )

    def reflect_edits(self, edited_md_file):
        # TODO:
        # ... [You'll need a new function here to parse the edited markdown and update the audio. It's complex and might involve word alignment] ...
        pass
