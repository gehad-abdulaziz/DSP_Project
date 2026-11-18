"""Runs the whole project.  Usage:  python main.py        (all parts)
                                    python main.py 3 4   (only parts 3 and 4)"""
import importlib
import sys
import traceback

PARTS = [
    "part1_dtft.dtft",
    "part2_convolution.convolution",
    "part3_audio_analysis.audio_analysis",
    "part4_audio_filtering.notch_audio",
    "part5_image_fourier.image_fourier",
    "part6_image_denoising.image_denoising",
]


def main():
    only = sys.argv[1:]
    for i, module in enumerate(PARTS, start=1):
        if only and str(i) not in only:
            continue
        print(f"\n=== Running part {i} ===")
        try:
            importlib.import_module(module).run()
        except Exception:
            traceback.print_exc()
    print("\nDone. Results are in outputs/")


if __name__ == "__main__":
    main()