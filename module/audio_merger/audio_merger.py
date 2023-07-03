from pydub import AudioSegment
import os

class AudioMerger:
    def __init__(self, directory, filenames, overlap_duration, output_path):
        self.directory = directory
        self.filenames = filenames
        self.overlap_duration = overlap_duration
        self.output_path = output_path

    def mix_and_overlap(self, sound1, sound2):
        overlap = sound2[:self.overlap_duration]
        mixed = sound1[-self.overlap_duration:].overlay(overlap)
        sound1 = sound1[:-self.overlap_duration] + mixed
        output = sound1 + sound2[self.overlap_duration:]
        return output

    def join_audio_files(self):
        first_file_path = os.path.join(self.directory, self.filenames[0])
        first_file_format = os.path.splitext(first_file_path)[1].replace(".", "")
        output = AudioSegment.from_file(first_file_path, format=first_file_format)

        for filename in self.filenames[1:]:
            file_path = os.path.join(self.directory, filename)
            file_format = os.path.splitext(file_path)[1].replace(".", "")
            sound = AudioSegment.from_file(file_path, format=file_format)
            output = self.mix_and_overlap(output, sound)

        return output

    def export(self):
        output = self.join_audio_files()
        output.export(self.output_path, format="wav")
