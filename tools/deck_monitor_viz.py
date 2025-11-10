"""
DJ Deck Monitor Visualization
Displays A/B/OUT spectrograms in vertical stack with playhead and crossfader overlays
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional, Tuple
from pathlib import Path
from tools.beat_spectrogram import BeatSpectrogramTool


class DeckMonitorVisualization:
    """
    Creates visual representation of DJ mixer state showing:
    - Deck A spectrogram (full RGB)
    - Deck B spectrogram (full RGB)
    - A+B Mix visualization (R+B channels = purple overlap)
    - Output spectrogram (full RGB, after EQ/FX)
    - Playhead position and crossfader overlay
    """

    def __init__(self):
        self.spec_tool = BeatSpectrogramTool()

    def generate(
        self,
        track_a_path: str,
        track_b_path: str,
        bpm_a: float,
        bpm_b: float,
        crossfader: float = 0.5,  # 0=full A, 1=full B
        playhead_a_seconds: Optional[float] = None,
        playhead_b_seconds: Optional[float] = None,
        beats_per_division: float = 0.25,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Generate deck monitor visualization.

        Args:
            track_a_path: Path to deck A audio
            track_b_path: Path to deck B audio
            bpm_a: Tempo of track A
            bpm_b: Tempo of track B
            crossfader: Position 0-1 (0=full A, 1=full B)
            playhead_a_seconds: Current position in track A
            playhead_b_seconds: Current position in track B
            beats_per_division: Musical resolution
            output_path: Where to save image

        Returns:
            Dict with visualization metadata and path
        """
        # Generate spectrograms for both tracks
        print("Generating Deck A spectrogram...")
        spec_data_a = self._generate_spectrogram_data(
            track_a_path, bpm_a, beats_per_division
        )

        print("Generating Deck B spectrogram...")
        spec_data_b = self._generate_spectrogram_data(
            track_b_path, bpm_b, beats_per_division
        )

        # Calculate A+B interaction (for purple visualization)
        spec_ab_mix = self._calculate_mix_output(
            spec_data_a, spec_data_b, crossfader, bpm_a, bpm_b
        )

        # Output is same as mix for now (until we add EQ/FX)
        # In future, this will show post-processing result
        spec_output = spec_ab_mix.copy()

        # Calculate playhead positions in divisions
        playhead_div_a = None
        playhead_div_b = None

        if playhead_a_seconds is not None:
            seconds_per_div = (60.0 / bpm_a) * beats_per_division
            playhead_div_a = int(playhead_a_seconds / seconds_per_div)

        if playhead_b_seconds is not None:
            seconds_per_div = (60.0 / bpm_b) * beats_per_division
            playhead_div_b = int(playhead_b_seconds / seconds_per_div)

        # Create visualization
        if output_path is None:
            output_path = "temp/deck_monitor.png"

        self._create_four_row_visualization(
            spec_data_a,
            spec_data_b,
            spec_ab_mix,
            spec_output,
            crossfader,
            playhead_div_a,
            playhead_div_b,
            bpm_a,
            bpm_b,
            beats_per_division,
            output_path
        )

        return {
            "output_path": output_path,
            "track_a": track_a_path,
            "track_b": track_b_path,
            "crossfader": crossfader,
            "playhead_a_seconds": playhead_a_seconds,
            "playhead_b_seconds": playhead_b_seconds,
            "spec_shape_a": list(spec_data_a.shape),
            "spec_shape_b": list(spec_data_b.shape),
            "spec_shape_ab_mix": list(spec_ab_mix.shape),
            "spec_shape_output": list(spec_output.shape)
        }

    def _generate_spectrogram_data(
        self,
        file_path: str,
        bpm: float,
        beats_per_division: float
    ) -> np.ndarray:
        """Generate spectrogram and return numpy array directly."""
        import librosa

        # Load audio
        y, sr = librosa.load(file_path, sr=self.spec_tool.sample_rate)

        # Compute mel spectrogram
        S_log_freq = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=self.spec_tool.n_fft,
            hop_length=self.spec_tool.hop_length,
            n_mels=self.spec_tool.freq_bins,
            fmin=self.spec_tool.freq_min,
            fmax=self.spec_tool.freq_max
        )
        S_log_freq_db = librosa.power_to_db(S_log_freq, ref=np.max)

        # Get time axis
        stft_times = librosa.frames_to_time(
            np.arange(S_log_freq_db.shape[1]),
            sr=sr,
            hop_length=self.spec_tool.hop_length
        )

        # Create beat grid
        duration = librosa.get_duration(y=y, sr=sr)
        seconds_per_beat = 60.0 / bpm
        seconds_per_division = seconds_per_beat * beats_per_division
        num_divisions = int(np.ceil(duration / seconds_per_division))
        time_grid = np.arange(num_divisions) * seconds_per_division

        # Quantize to beat grid
        return self._quantize_to_beat_grid(S_log_freq_db, stft_times, time_grid)

    def _quantize_to_beat_grid(
        self,
        spectrogram: np.ndarray,
        stft_times: np.ndarray,
        time_grid: np.ndarray
    ) -> np.ndarray:
        """Quantize spectrogram to beat grid (copied from beat_spectrogram.py)."""
        freq_bins, num_frames = spectrogram.shape
        num_divisions = len(time_grid)

        quantized = np.zeros((freq_bins, num_divisions))

        for i in range(num_divisions):
            start_time = time_grid[i]
            end_time = time_grid[i+1] if i+1 < num_divisions else stft_times[-1] + 1

            mask = (stft_times >= start_time) & (stft_times < end_time)

            if np.any(mask):
                quantized[:, i] = np.mean(spectrogram[:, mask], axis=1)
            else:
                quantized[:, i] = 0

        return quantized

    def _calculate_mix_output(
        self,
        spec_a: np.ndarray,
        spec_b: np.ndarray,
        crossfader: float,
        bpm_a: float,
        bpm_b: float
    ) -> np.ndarray:
        """
        Calculate mix output spectrogram based on crossfader position.

        Handles BPM differences by time-stretching to align grids.
        """
        # Crossfade weights
        weight_a = 1.0 - crossfader
        weight_b = crossfader

        # If BPMs match, simple weighted sum
        if abs(bpm_a - bpm_b) < 1.0:
            # Align to shorter length
            min_len = min(spec_a.shape[1], spec_b.shape[1])
            spec_a_aligned = spec_a[:, :min_len]
            spec_b_aligned = spec_b[:, :min_len]

            return weight_a * spec_a_aligned + weight_b * spec_b_aligned

        # Different BPMs - need to time-stretch one to match the other
        # For simplicity, stretch to match track A's grid
        target_len = spec_a.shape[1]

        # Resample spec_b to match spec_a's time grid
        from scipy.ndimage import zoom
        zoom_factor = target_len / spec_b.shape[1]
        spec_b_stretched = zoom(spec_b, (1.0, zoom_factor), order=1)

        # Ensure same length
        min_len = min(spec_a.shape[1], spec_b_stretched.shape[1])
        spec_a_aligned = spec_a[:, :min_len]
        spec_b_aligned = spec_b_stretched[:, :min_len]

        return weight_a * spec_a_aligned + weight_b * spec_b_aligned

    def _create_four_row_visualization(
        self,
        spec_a: np.ndarray,
        spec_b: np.ndarray,
        spec_ab_mix: np.ndarray,
        spec_output: np.ndarray,
        crossfader: float,
        playhead_div_a: Optional[int],
        playhead_div_b: Optional[int],
        bpm_a: float,
        bpm_b: float,
        beats_per_division: float,
        output_path: str
    ):
        """
        Create four-row visualization:
        - Deck A (full RGB magma)
        - Deck B (full RGB magma)
        - A+B Mix (R+B = purple showing overlap)
        - Output (full RGB magma, post-EQ/FX)
        """
        fig, (ax_a, ax_b, ax_mix, ax_out) = plt.subplots(
            4, 1,
            figsize=(20, 16),
            gridspec_kw={'height_ratios': [1, 1, 1, 1]}
        )

        # Deck A and B: Full RGB using magma colormap
        im_a = ax_a.imshow(spec_a, aspect='auto', origin='lower', cmap='magma', interpolation='nearest')
        im_b = ax_b.imshow(spec_b, aspect='auto', origin='lower', cmap='magma', interpolation='nearest')

        # A+B Mix: Purple visualization (R=A, B=B, overlap=purple)
        spec_ab_purple = self._create_purple_mix_visualization(spec_a, spec_b, crossfader)
        ax_mix.imshow(spec_ab_purple, aspect='auto', origin='lower')

        # Output: Full RGB using magma (will differ from A+B when EQ/FX added)
        im_out = ax_out.imshow(spec_output, aspect='auto', origin='lower', cmap='magma', interpolation='nearest')

        # Configure axes
        for ax, label in [(ax_a, 'DECK A'), (ax_b, 'DECK B'), (ax_mix, 'A+B MIX'), (ax_out, 'OUTPUT')]:
            ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
            ax.set_title(label, fontsize=14, fontweight='bold', pad=10)

            # Frequency labels
            freq_labels = ['60Hz', '250Hz', '1kHz', '4kHz', '16kHz']
            freq_positions = np.linspace(0, 127, len(freq_labels))
            ax.set_yticks(freq_positions)
            ax.set_yticklabels(freq_labels)

        # Only bottom gets x-axis label
        ax_out.set_xlabel('Musical Time (Bars)', fontsize=12, fontweight='bold')

        # Add bar markers (assuming 4/4 time)
        beats_per_bar = 4
        divisions_per_bar = int(beats_per_bar / beats_per_division)

        for ax, spec in [(ax_a, spec_a), (ax_b, spec_b), (ax_mix, spec_ab_mix), (ax_out, spec_output)]:
            num_divisions = spec.shape[1]
            bar_positions = np.arange(0, num_divisions, divisions_per_bar)
            bar_labels = [f"Bar {i+1}" for i in range(len(bar_positions))]

            ax.set_xticks(bar_positions[::4])  # Every 4 bars
            ax.set_xticklabels(bar_labels[::4], rotation=45)

        # Playhead overlays (vertical lines across all rows)
        for ax in [ax_a, ax_b, ax_mix, ax_out]:
            if playhead_div_a is not None:
                ax.axvline(playhead_div_a, color='white', linewidth=2,
                          linestyle='--', alpha=0.8)
            if playhead_div_b is not None:
                ax.axvline(playhead_div_b, color='cyan', linewidth=2,
                          linestyle='--', alpha=0.8)

        # Crossfader overlay on A+B MIX row
        mix_height = spec_ab_mix.shape[0]
        crossfade_y = mix_height * (1 - crossfader)

        ax_mix.axhline(crossfade_y, color='yellow', linewidth=3,
                       linestyle='-', alpha=0.9,
                       label=f'Crossfader')

        # Crossfader annotation
        ax_mix.text(
            spec_ab_mix.shape[1] * 0.02, crossfade_y,
            f"←A {int((1-crossfader)*100)}% | {int(crossfader*100)}% B→",
            color='yellow', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.8)
        )

        # BPM annotations
        ax_a.text(0.02, 0.95, f'{bpm_a:.1f} BPM', transform=ax_a.transAxes,
                 color='white', fontsize=10, fontweight='bold',
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        ax_b.text(0.02, 0.95, f'{bpm_b:.1f} BPM', transform=ax_b.transAxes,
                 color='white', fontsize=10, fontweight='bold',
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        # Legend
        ax_mix.legend(loc='upper right', fontsize=9)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.close()

        print(f"✅ Deck monitor visualization saved: {output_path}")

    def _create_purple_mix_visualization(
        self,
        spec_a: np.ndarray,
        spec_b: np.ndarray,
        crossfader: float
    ) -> np.ndarray:
        """
        Create R+B purple visualization showing A/B overlap.

        Red channel = Track A (weighted by crossfader)
        Blue channel = Track B (weighted by crossfader)
        Purple = overlap (both playing)
        """
        # Normalize both specs to 0-1
        spec_a_norm = (spec_a - spec_a.min()) / (spec_a.max() - spec_a.min() + 1e-8)

        # Align B to A's length
        if spec_b.shape[1] != spec_a.shape[1]:
            from scipy.ndimage import zoom
            zoom_factor = spec_a.shape[1] / spec_b.shape[1]
            spec_b = zoom(spec_b, (1.0, zoom_factor), order=1)

        spec_b_norm = (spec_b - spec_b.min()) / (spec_b.max() - spec_b.min() + 1e-8)

        # Apply crossfader weighting
        weight_a = 1.0 - crossfader
        weight_b = crossfader

        # Create RGB array
        h, w = spec_a_norm.shape
        rgb = np.zeros((h, w, 3))

        rgb[:, :, 0] = spec_a_norm * weight_a  # Red = Track A
        rgb[:, :, 2] = spec_b_norm * weight_b  # Blue = Track B
        # Purple appears where both are active

        return rgb

    def _apply_color_tint(self, spectrogram: np.ndarray, color: str) -> np.ndarray:
        """
        Convert grayscale spectrogram to RGB with color tint.
        """
        # Normalize to 0-1 range
        spec_norm = (spectrogram - spectrogram.min()) / (spectrogram.max() - spectrogram.min() + 1e-8)

        # Create RGB array
        h, w = spectrogram.shape
        rgb = np.zeros((h, w, 3))

        if color == 'red':
            rgb[:, :, 0] = spec_norm  # Red channel
            rgb[:, :, 1] = spec_norm * 0.2  # Slight green for visibility
            rgb[:, :, 2] = spec_norm * 0.2  # Slight blue for visibility
        elif color == 'green':
            rgb[:, :, 0] = spec_norm * 0.2
            rgb[:, :, 1] = spec_norm  # Green channel
            rgb[:, :, 2] = spec_norm * 0.2
        elif color == 'blue':
            rgb[:, :, 0] = spec_norm * 0.2
            rgb[:, :, 1] = spec_norm * 0.2
            rgb[:, :, 2] = spec_norm  # Blue channel

        return rgb


def create_deck_monitor_visualization(
    track_a_path: str,
    track_b_path: str,
    bpm_a: float,
    bpm_b: float,
    crossfader: float = 0.5,
    playhead_a_seconds: Optional[float] = None,
    playhead_b_seconds: Optional[float] = None,
    output_path: Optional[str] = None
) -> Dict:
    """
    Convenience function for creating deck monitor visualization.

    Args:
        track_a_path: Path to deck A audio
        track_b_path: Path to deck B audio
        bpm_a: Tempo of track A
        bpm_b: Tempo of track B
        crossfader: Position 0-1 (0=full A, 1=full B)
        playhead_a_seconds: Current playback position in track A
        playhead_b_seconds: Current playback position in track B
        output_path: Optional output image path

    Returns:
        Dict with visualization metadata
    """
    viz = DeckMonitorVisualization()
    return viz.generate(
        track_a_path, track_b_path,
        bpm_a, bpm_b,
        crossfader,
        playhead_a_seconds, playhead_b_seconds,
        output_path=output_path
    )


if __name__ == "__main__":
    print("DJ Deck Monitor Visualization")
    print("Usage:")
    print("  from tools.deck_monitor_viz import create_deck_monitor_visualization")
    print("  result = create_deck_monitor_visualization(")
    print("      'music/track_a.mp3', 'music/track_b.mp3',")
    print("      bpm_a=128, bpm_b=130, crossfader=0.35)")
