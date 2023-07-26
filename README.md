# LyricWhiz

[![arXiv](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)](https://arxiv.org/abs/2306.17103)

Official code for the paper: LyricWhiz: Robust Multilingual Zero-shot Lyrics Transcription by Whispering to ChatGPT. 
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

