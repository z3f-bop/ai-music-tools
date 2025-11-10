"""
Beat-Quantized Spectrogram Generator
Generates spectrograms where time axis is aligned to musical beats/divisions
instead of linear seconds.
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional, Tuple
from pathlib import Path
import json


class BeatSpectrogramTool:
    """
    Generate beat-synchronized spectrograms showing full frequency spectrum
    quantized to musical time divisions.
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        n_fft: int = 2048,
        hop_length: int = 512,
        freq_bins: int = 128,
        freq_min: float = 20.0,
        freq_max: float = 20000.0
    ):
        """
        Args:
            sample_rate: Audio sample rate
            n_fft: FFT window size
            hop_length: Hop length for STFT
            freq_bins: Number of frequency bins in output (logarithmic)
            freq_min: Minimum frequency (Hz)
            freq_max: Maximum frequency (Hz)
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.freq_bins = freq_bins
        self.freq_min = freq_min
        self.freq_max = freq_max

    def generate(
        self,
        file_path: str,
        bpm: float,
        beats_per_division: float = 0.25,  # 1/16th note = 0.25 beats
        output_path: Optional[str] = None,
        save_data: bool = True,
        save_image: bool = True
    ) -> Dict:
        """
        Generate beat-quantized spectrogram.

        Args:
            file_path: Path to audio file
            bpm: Tempo in beats per minute
            beats_per_division: Musical resolution (0.25 = 1/16th, 0.5 = 1/8th, etc.)
            output_path: Base path for output files (without extension)
            save_data: Save JSON data file
            save_image: Save PNG image

        Returns:
            Dict with spectrogram data and metadata
        """
        # Load audio
        y, sr = librosa.load(file_path, sr=self.sample_rate)
        duration = librosa.get_duration(y=y, sr=sr)

        # Beat tracking
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, bpm=bpm)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Calculate time grid based on musical divisions
        seconds_per_beat = 60.0 / bpm
        seconds_per_division = seconds_per_beat * beats_per_division
        num_divisions = int(np.ceil(duration / seconds_per_division))
        time_grid = np.arange(num_divisions) * seconds_per_division

        # Compute STFT
        D = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
        S = np.abs(D)  # Magnitude spectrogram

        # Convert to dB scale
        S_db = librosa.amplitude_to_db(S, ref=np.max)

        # Get time axis for STFT frames
        stft_times = librosa.frames_to_time(
            np.arange(S.shape[1]),
            sr=sr,
            hop_length=self.hop_length
        )

        # Create logarithmic frequency bins
        freq_axis = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)

        # Map to logarithmic mel-like scale
        S_log_freq = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.freq_bins,
            fmin=self.freq_min,
            fmax=self.freq_max
        )
        S_log_freq_db = librosa.power_to_db(S_log_freq, ref=np.max)

        # Quantize to beat grid
        beat_quantized_spec = self._quantize_to_beat_grid(
            S_log_freq_db,
            stft_times,
            time_grid
        )

        # Prepare output
        result = {
            "file_path": file_path,
            "bpm": float(bpm),
            "duration": float(duration),
            "beats_per_division": beats_per_division,
            "seconds_per_division": float(seconds_per_division),
            "num_divisions": int(num_divisions),
            "freq_bins": self.freq_bins,
            "freq_min": float(self.freq_min),
            "freq_max": float(self.freq_max),
            "spectrogram_shape": list(beat_quantized_spec.shape),
            "beat_times": beat_times.tolist()
        }

        # Generate output path if not provided
        if output_path is None:
            file_stem = Path(file_path).stem
            output_path = f"temp/{file_stem}_beat_spec"

        # Save data
        if save_data:
            data_path = f"{output_path}.json"
            np.save(f"{output_path}.npy", beat_quantized_spec)
            with open(data_path, 'w') as f:
                json.dump(result, f, indent=2)
            result["data_path"] = data_path
            result["numpy_path"] = f"{output_path}.npy"

        # Save image
        if save_image:
            image_path = f"{output_path}.png"
            self._save_visualization(
                beat_quantized_spec,
                time_grid,
                bpm,
                beats_per_division,
                image_path
            )
            result["image_path"] = image_path

        # Include actual data if not saving to file
        if not save_data:
            result["spectrogram_data"] = beat_quantized_spec.tolist()

        return result

    def _quantize_to_beat_grid(
        self,
        spectrogram: np.ndarray,
        stft_times: np.ndarray,
        time_grid: np.ndarray
    ) -> np.ndarray:
        """
        Quantize spectrogram to beat grid by averaging within each time division.

        Args:
            spectrogram: [freq_bins, time_frames] spectrogram
            stft_times: Time in seconds for each STFT frame
            time_grid: Target beat-quantized time grid

        Returns:
            [freq_bins, num_divisions] beat-quantized spectrogram
        """
        freq_bins, num_frames = spectrogram.shape
        num_divisions = len(time_grid)

        # Initialize output
        quantized = np.zeros((freq_bins, num_divisions))

        # For each time division, average all STFT frames within that division
        for i in range(num_divisions):
            # Define time window for this division
            start_time = time_grid[i]
            end_time = time_grid[i+1] if i+1 < num_divisions else stft_times[-1] + 1

            # Find STFT frames within this window
            mask = (stft_times >= start_time) & (stft_times < end_time)

            if np.any(mask):
                # Average spectral content within this division
                quantized[:, i] = np.mean(spectrogram[:, mask], axis=1)
            else:
                # No frames in this division (edge case)
                quantized[:, i] = 0

        return quantized

    def _save_visualization(
        self,
        spectrogram: np.ndarray,
        time_grid: np.ndarray,
        bpm: float,
        beats_per_division: float,
        output_path: str
    ):
        """
        Create and save visualization of beat-quantized spectrogram.

        Args:
            spectrogram: [freq_bins, num_divisions] array
            time_grid: Time axis in seconds
            bpm: Tempo
            beats_per_division: Musical resolution
            output_path: Output PNG path
        """
        fig, ax = plt.subplots(figsize=(16, 8))

        # Display spectrogram
        img = ax.imshow(
            spectrogram,
            aspect='auto',
            origin='lower',
            cmap='magma',
            interpolation='nearest'
        )

        # Configure axes
        num_divisions = spectrogram.shape[1]

        # X-axis: musical time (bars/beats)
        beats_per_bar = 4  # Assume 4/4 time
        divisions_per_bar = int(beats_per_bar / beats_per_division)

        # Create x-tick labels showing bar numbers
        bar_positions = np.arange(0, num_divisions, divisions_per_bar)
        bar_labels = [f"Bar {i//divisions_per_bar + 1}" for i in bar_positions]
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(bar_labels, rotation=45)

        # Y-axis: frequency bins (logarithmic scale)
        freq_labels = [f"{int(f)}Hz" for f in np.logspace(
            np.log10(self.freq_min),
            np.log10(self.freq_max),
            num=10
        )]
        freq_positions = np.linspace(0, self.freq_bins-1, len(freq_labels))
        ax.set_yticks(freq_positions)
        ax.set_yticklabels(freq_labels)

        # Labels and title
        division_name = {
            0.25: "16th notes",
            0.5: "8th notes",
            1.0: "quarter notes",
            2.0: "half notes"
        }.get(beats_per_division, f"{beats_per_division} beats")

        ax.set_xlabel("Musical Time (Bars)")
        ax.set_ylabel("Frequency")
        ax.set_title(f"Beat-Quantized Spectrogram\n{bpm:.1f} BPM, {division_name} resolution")

        # Colorbar
        cbar = plt.colorbar(img, ax=ax)
        cbar.set_label("Amplitude (dB)")

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()


def beat_spectrogram_tool(
    file_path: str,
    bpm: float,
    beats_per_division: float = 0.25,
    output_path: Optional[str] = None
) -> Dict:
    """
    Convenience function for generating beat-quantized spectrograms.

    Args:
        file_path: Path to audio file
        bpm: Tempo in beats per minute
        beats_per_division: Musical resolution (0.25 = 1/16th note)
        output_path: Optional output path base

    Returns:
        Dict with spectrogram data and output paths
    """
    tool = BeatSpectrogramTool()
    return tool.generate(file_path, bpm, beats_per_division, output_path)


if __name__ == "__main__":
    # Example usage
    print("Beat-Quantized Spectrogram Generator")
    print("Usage:")
    print("  from tools.beat_spectrogram import beat_spectrogram_tool")
    print("  result = beat_spectrogram_tool('track.mp3', bpm=128, beats_per_division=0.25)")
