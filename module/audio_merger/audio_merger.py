# from pydub import AudioSegment
# import os

# class AudioMerger:
#     def __init__(self, directory, filenames, overlap_duration, output_path):
#         self.directory = directory
#         self.filenames = filenames
#         self.overlap_duration = overlap_duration
#         self.output_path = output_path

#     def mix_and_overlap(self, sound1, sound2):
#         # Overlap the two sounds
#         overlap = sound2[:self.overlap_duration]
#         sound1_end = sound1[-self.overlap_duration:]
#         sound1 = sound1[:-self.overlap_duration]

#         # Crossfade
#         crossfaded = sound1_end.append(overlap, crossfade=self.overlap_duration)

#         # Fade out the end of the first sound, fade in the beginning of the second sound
#         sound1 = sound1.fade_out(self.overlap_duration)
#         sound2 = sound2.fade_in(self.overlap_duration)

#         # Combine everything
#         output = sound1 + crossfaded + sound2[self.overlap_duration:]
#         return output
    
#     def join_audio_files(self):
#         first_file_path = os.path.join(self.directory, self.filenames[0])
#         first_file_format = os.path.splitext(first_file_path)[1].replace(".", "")
#         output = AudioSegment.from_file(first_file_path, format=first_file_format)

#         for filename in self.filenames[1:]:
#             file_path = os.path.join(self.directory, filename)
#             file_format = os.path.splitext(file_path)[1].replace(".", "")
#             sound = AudioSegment.from_file(file_path, format=file_format)
#             output = self.mix_and_overlap(output, sound)

#         return output

#     def export(self):
#         output = self.join_audio_files()
#         output.export(self.output_path, format="wav")

from pydub import AudioSegment
from pydub.generators import WhiteNoise
import os

class AudioMerger:
    
    def __init__(self, directory, filenames, overlap_duration, output_path):
        self.segments = [AudioSegment.from_file(os.path.join(directory, file)) for file in filenames]
        self.overlap_duration = overlap_duration
        self.output_path = output_path

    def _match_volumes(self, seg_a, seg_b, duration_ms):
        avg_vol_a = seg_a[-duration_ms:].dBFS
        avg_vol_b = seg_b[:duration_ms].dBFS
        volume_difference = avg_vol_a - avg_vol_b
        return seg_b + volume_difference

    def _add_white_noise(self, segment, duration_ms):
        noise = WhiteNoise().to_audio_segment(duration=duration_ms, volume=-50)
        return segment.append(noise, crossfade=0)

    def merge(self):
        combined = self.segments[0]

        for i in range(1, len(self.segments)):
            self.segments[i] = self._match_volumes(combined, self.segments[i], self.overlap_duration)
            combined = combined.append(self.segments[i], crossfade=self.overlap_duration)

        return combined

    def export(self):
        combined_audio = self.merge()
        combined_audio.export(self.output_path, format="wav")
