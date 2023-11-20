# LyricWhiz

[![arXiv](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)](https://arxiv.org/abs/2306.17103)

[ISMIR 2023] Official code for the paper: LyricWhiz: Robust Multilingual Zero-shot Lyrics Transcription by Whispering to ChatGPT. 
Welcome to visit our [m-a-p community](https://https://m-a-p.ai/) and [MARBLE benchmark](https://marble-bm.sheffield.ac.uk/) for more details.

## MulJam-Dataset

We introduce the first large-scale, weakly supervised, and copyright-free multilingual lyric transcription dataset, MulJam, consisting of 6,031 songs with 182,429 lines and a total duration of 381.9 hours. The dataset is placed under the `./MulJam` folder.

## Setup

To install the dependencies, run the following command:
```
pip install -r requirements.txt
```

## Whisper Transcription

To transcribe lyrics using Whisper, run the following command:
```
sh code/run.sh
```

## ChatGPT Post-Processing

To post-process the Whisper output using ChatGPT, run the corresponding Python script in the `./code` folder:

## Update: MulJam v2.0

MulJam v2.0 differs in two aspects:
1. We have increased the test set size and collected refined human lyrics annotations, leading to adjustments in the data split.
2. We have excluded the songs from the training and validation sets that were present in [Jamendo](https://github.com/f90/jamendolyrics).
This exclusion enables a valid comparison with other lyrics transcription systems on the Jamendo dataset.

For a detailed description of MulJam v2.0, please refer to appendix E of the [MARBLE benchmark paper](https://openreview.net/attachment?id=2s7ZZUhEGS&name=pdf).

## Getting the Audio

The script for downloading and preprocessing audio will be available in the [MARBLE benchmark repository](https://github.com/a43992899/MARBLE-Benchmark).

## Citation

If you find this repository useful, please cite our paper:
```
@article{zhuo2023lyricwhiz,
  title={LyricWhiz: Robust Multilingual Zero-shot Lyrics Transcription by Whispering to ChatGPT},
  author={Zhuo, Le and Yuan, Ruibin and Pan, Jiahao and Ma, Yinghao and LI, Yizhi and Zhang, Ge and Liu, Si and Dannenberg, Roger and Fu, Jie and Lin, Chenghua and others},
  journal={arXiv preprint arXiv:2306.17103},
  year={2023}
}
```

