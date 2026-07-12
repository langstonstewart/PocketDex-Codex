
import os
import wave
from src.resource_path import resource_path
from PyQt6.QtCore import QIODevice, QByteArray, QBuffer
from PyQt6.QtMultimedia import QAudioSink, QAudioFormat

class MediaManager:
    def __init__(self) -> None:
        self.audio_sink = None
        self.audio_buffer = None
        self.play_cry("0001", 0.0)

    def play_cry(self, dex_num, vol):
        file_path = resource_path(f"src\\media\\cries\\cry_{dex_num}.wav")
        
        if not os.path.exists(file_path):
            print(f"Error: Cry file not found ({file_path})")
            return

        try:
            with wave.open(file_path, 'rb') as wav_file:
                channels = wav_file.getnchannels()
                sample_rate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()
                raw_frames = wav_file.readframes(wav_file.getnframes())

            audio_format = QAudioFormat()
            audio_format.setChannelCount(channels)
            audio_format.setSampleRate(sample_rate)
            
            if sample_width == 1:
                audio_format.setSampleFormat(QAudioFormat.SampleFormat.UInt8)
            elif sample_width == 2:
                audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
            elif sample_width == 4:
                audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int32)
            else:
                print("Unsupported WAV format layout")
                return

            if self.audio_sink:
                self.audio_sink.stop()

            self.audio_sink = QAudioSink(audio_format)
            self.audio_sink.setVolume(vol)

            self.audio_buffer = QBuffer()
            self.audio_buffer.setData(QByteArray(raw_frames))
            self.audio_buffer.open(QIODevice.OpenModeFlag.ReadOnly)

            self.audio_sink.start(self.audio_buffer)
        except Exception as e:
            print(f"Failed to play cry: {e}")
