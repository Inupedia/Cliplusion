from module import *


def main():
    directory = "./src/input"
    filenames = ["1.m4a", "2.m4a", "3.m4a"]
    overlap_duration = 500
    output_path = "./src/output/output.wav"

    audio_merger = AudioMerger(directory, filenames, overlap_duration, output_path)
    audio_merger.export()

    audio_transcriber = AudioTranscriber(directory, output_path)
    audio_transcriber.export()


if __name__ == "__main__":
    main()
