import jiwer
import pprint
import os
import re
import json
import sys
import numpy as np
from tools.utils import remove_emoji, get_song_list, compute_wer, convert_digits_to_words
from tools.utils import LANGUAGES, transformation


def add_song(song_name, _dict, all, pred_dir, gt_dir):
    _dict[song_name] = {}

    # transcribed = os.path.join(pred_dir, f'{song_name}.{"json" if content_type == "json" else "gptrlt.txt"}')
    # with open(transcribed, 'r') as _file:
    #     if content_type == 'json':
    #         t_text = json.load(_file)['output']
    #     else:
    #         t_text = _file.read()
            # t_text = json.loads(t_text)['output']

    ## compare whisper result with ground truth
    transcribed = os.path.join(pred_dir, song_name + '.wav.json')
    with open(transcribed, 'r') as _file:
        t_segs = json.load(_file)['segments']
        t_text = []
        for seg in t_segs:
            if seg['no_speech_prob'] < 0.9:
                t_text.append(seg['text'])
    t_text = ' '.join(t_text)


    official = os.path.join(gt_dir, f'{song_name}.txt')
    with open(official, 'r') as _file:
        o_text = _file.read()

    # post processing of the text
    t_text = t_text.lower()
    t_text = t_text.replace('\n', ' ')
    t_text = remove_emoji(t_text)
    t_text = t_text.replace(' am', 'm')
    t_text = t_text.replace('\'d', ' would')
    t_text = transformation(t_text)
    t_text = convert_digits_to_words(t_text)
    o_text = o_text.lower()
    o_text = o_text.replace('\n', ' ')
    o_text = remove_emoji(o_text)
    o_text = o_text.replace(' am', 'm')
    o_text = o_text.replace('\'d', ' would')
    o_text = transformation(o_text)
    o_text = convert_digits_to_words(o_text)

    # post processing of for the ground truth
    for i, word in enumerate(o_text):
        if word[-2:] == 'in' and len(word) > 2:
            o_text[i] = word[:-2] + 'ing'

    errors = jiwer.compute_measures(truth=o_text, hypothesis=t_text)
    _dict[song_name]['mer'] = errors['mer']
    _dict[song_name]['wer'] = errors['wer']
    _dict[song_name]['wil'] = errors['wil']
    _dict[song_name]['wip'] = errors['wip']
    all['mer'] += errors['mer']
    all['wer'] += errors['wer']
    all['wil'] += errors['wil']
    all['wip'] += errors['wip']
    
    print()
    print(song_name, "WER: ", errors['wer'])
    print("Prediction: ", len(t_text))
    print(t_text)
    print("Ground truth: ", len(o_text))
    print(o_text)


def main():
    songlist_file = sys.argv[1]
    pred_dir = sys.argv[2]
    content_type = sys.argv[3]
    gt_dir = sys.argv[4]
    results = {}

    all = {'mer': 0, 'wer': 0, 'wil': 0, 'wip': 0, 'wer2': 0}
    songs = get_song_list(songlist_file)
    for song in songs:
        add_song(song, results, all, pred_dir, gt_dir)
    # pprint.pprint(results)

    
    # for entry in results:
    #     print(entry)
    #     for er in results[entry]:
    #         print(f"\t{er} {results[entry][er]}")

    print("total songs: ", len(songs))
    print("mer mean: ", all['mer']/len(songs))
    print("wer mean: ", all['wer']/len(songs))
    print("wil mean: ", all['wil']/len(songs))
    print("wip mean: ", all['wip']/len(songs))

if __name__ == '__main__':
    main()
