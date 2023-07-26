import argparse
import os
import json
from tqdm import tqdm

import librosa
import numpy as np
import torch

from panns_inference import AudioTagging, SoundEventDetection, labels
import whisper


def find_audios(parent_dir, exts=['.wav', '.mp3', '.flac', '.webm', '.mp4', '.m4a']):
    audio_files = []
    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            if os.path.splitext(file)[1] in exts:
                audio_files.append(os.path.join(root, file))
    return audio_files


#################### PANNs ####################

def load_panns(device='cuda'):
    model = AudioTagging(checkpoint_path=None, device=device)
    return model

@torch.no_grad()
def tag_audio(model, audio_path):
    (audio, _) = librosa.core.load(audio_path, sr=32000, mono=True)
    # only use the first 30 seconds
    audio = audio[None, :30*32000]
    (clipwise_output, embedding) = model.inference(audio)
    tags, probs = get_audio_tagging_result(clipwise_output[0])
    return tags, probs


def get_audio_tagging_result(clipwise_output):
    """Visualization of audio tagging result.
    Args:
      clipwise_output: (classes_num,)
    """
    sorted_indexes = np.argsort(clipwise_output)[::-1]

    tags = []
    probs = []
    for k in range(10):
        tag = np.array(labels)[sorted_indexes[k]]
        prob = clipwise_output[sorted_indexes[k]]
        tags.append(tag)
        probs.append(float(prob))

    return tags, probs 


def is_vocal(tags, probs, threshold=0.08):
    pos_tags = {'Speech', 'Singing', 'Rapping'}
    for tag, prob in zip(tags, probs):
        if tag in pos_tags and prob > threshold:
            return True
    return False


#################### Whisper ####################


def load_whisper(model="large"):
    model = whisper.load_model(model, in_memory=True)
    return model


def transcribe_and_save(whisper_model, panns_model, args):
    """transcribe the audio, and save the result with the same relative path in the output_dir
    """
    audio_files = find_audios(args.input_dir)

    if args.n_shard > 1:
        print(f'processing shard {args.shard_rank} of {args.n_shard}')
        audio_files.sort() # make sure no intersetction
        audio_files = audio_files[args.shard_rank * len(audio_files) // args.n_shard : (args.shard_rank + 1) * len(audio_files) // args.n_shard] 

    for file in tqdm(audio_files):
        output_file = os.path.join(args.output_dir, os.path.relpath(file, args.input_dir))
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        result = {}
        try:
            tags, probs = tag_audio(panns_model, file)

            if args.threshold == 0. or is_vocal(tags, probs, threshold=args.threshold):
                if args.debug:
                    print(file)
                    for tag, prob in zip(tags, probs):
                        print(f'{tag}: {prob}')
                    continue
                
                result = whisper.transcribe(whisper_model, file, language=args.language, initial_prompt=args.prompt)
                result['tags_with_probs'] = [{'tag': tag, 'prob': prob} for tag, prob in zip(tags, probs)]
                with open(output_file + '.json', 'w') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
            else:
                print(f'no vocal in {file}')
                if args.debug:
                    for tag, prob in zip(tags, probs):
                            print(f'{tag}: {prob}')

        except Exception as e:
            print(e)
            continue
        
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='large', help='model name')
    parser.add_argument('--prompt', type=str, default='lyrics: ', help='prompt for transcription')
    parser.add_argument('--language', type=str, default='en', help='language of target audio')
    parser.add_argument('--input_dir', type=str, default='./data', help='input directory')
    parser.add_argument('--output_dir', type=str, default='./results', help='output directory')
    parser.add_argument('--n_shard', type=int, default=1, help='number of shards')
    parser.add_argument('--shard_rank', type=int, default=0, help='rank of this shard')
    parser.add_argument('--threshold', type=float, default=0.00, help='threshold for vocal detection')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    whisper_model = load_whisper(args.model)
    panns_model = load_panns()
    transcribe_and_save(whisper_model, panns_model, args)

if __name__ == '__main__':
    main()
