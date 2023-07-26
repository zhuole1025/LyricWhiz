import json
import os
import sys
import time
import argparse 
import random
import re 
from collections import Counter

import openai

from config.chatgpt_config import config_dict
from tools.cfg_wrapper import load_config
from tools.utils import remove_emoji, LANGUAGES

add_songname=False
add_language=True

def concat_lyrics(whisper_rlts, content_type, song_name):
    if content_type == 'txt':
        lyrics = ""
        for i, rlt in enumerate(whisper_rlts):
            lyrics += f'\nRecognition Result {str(i+1)}: \" {rlt}" '
    elif content_type == 'json':
        lyrics = dict()
        if add_songname:
            lyrics['song_name'] = get_song_name(song_name)
        for i, o in enumerate(whisper_rlts):
            lyrics[f"prediction_{i+1}"] = o
        lyrics = json.dumps(lyrics, ensure_ascii=False)
    return lyrics, len(whisper_rlts)

def get_whisper_pred(song_name, whisper_rlts_dir, time_stamp=False, audio_type="wav"):
    whisper_rlts = []
    # for i in range(num_samples):
    cnt = 0
    prediction_dirs = [
    # "whisper_l",
    # "whisper_l_2",
    # "whisper_l_3",
    # "whisper_l_4",
    # "whisper_l_5",
    # "whisper_l_prompt",
    # "whisper_l_prompt_2",
    # "whisper_l_prompt_3",
    # "whisper_l_prompt_4",
    # "whisper_l_prompt_5",
    # "whisper_prompt_1",
    # "whisper_prompt_2",
    # "whisper_prompt_3",
    # "whisper_prompt_4",
    # "whisper_prompt_5",
    "whisper_1",
    "whisper_2",
    "whisper_3",
    "whisper_4",
    "whisper_5",
    # "mask_prompt_1",
    # "mask_prompt_2",
    # "mask_prompt_3",
    # "mask_prompt_4",
    # "mask_prompt_5",
    ]
    languages=[]
    for prediction_dir in prediction_dirs:
        json_path = os.path.join(whisper_rlts_dir, prediction_dir, song_name + f'.{audio_type}.json')
        with open(json_path) as json_file:
            data = json.load(json_file)
        segments = data['segments']
        languages.append(LANGUAGES[data['language']])
        out = ""
        for segment in segments:
            if segment['no_speech_prob'] > 0.9:
                continue
            text = segment['text'].strip().replace('\t', ' ')
            # text = remove_emoji(text)
            start = float(segment['start'])
            end = float(segment['end'])
            # keep two decimal places
            start = "{:.2f}".format(start)
            end = "{:.2f}".format(end)
            if time_stamp:
                out += (f"[{start}:{end}]\t{text}\n")
            else:
                out += (f"{text}\n") 
        whisper_rlts.append(out)
    
    language = Counter(languages).most_common(1)[0][0]
    return whisper_rlts, language

def sample_n_predictions(whisper_rlts_list, n=3):
    return random.sample(whisper_rlts_list, n)

def ensemble_whisper(song_name, whisper_rlts_dir, sample_num, content_type, audio_type):
    rand_sample = True

    whisper_rlts, language = get_whisper_pred(song_name, whisper_rlts_dir, time_stamp=False, audio_type=audio_type)
    if rand_sample:
        whisper_rlts = sample_n_predictions(whisper_rlts, sample_num)
    else:
        whisper_rlts = whisper_rlts[:sample_num]
    concated_lyrics, num_lyrics = concat_lyrics(whisper_rlts, content_type, song_name)

    return concated_lyrics, num_lyrics, language

def get_request_msg(prompt, concated_lyrics, language):
    # request_msg=[
    #           {
    #            "role": "system",
    #            "content": prompt['prefix']
    #           },
    #         {
    #           "role": "user", 
    #           "content": requests_ctx
    #          }
    # ],

    request_msg=[
        {
            "role": "user", 
            "content": prompt['prefix'] + ' ' + concated_lyrics + '\n' + prompt['suffix']
        },
    ]

    return request_msg

def requests_chatgpt(request_msg, apikey, model_name):
    openai.api_key = apikey

    completion = openai.ChatCompletion.create(
        model=model_name,
        messages = request_msg,
    )

    resp = completion.choices[0].message["content"]
    return resp

def extract_json(str):
    match = re.search(r'{.*}', str)
    if match:
        return match.group(0)
    else:
        return {"output":""}

def save_resp(resp, content_type, output_dir, song_name):
    song_name = song_name.replace("/","_")
    if content_type == "txt":
        gptrlt_file = os.path.join(output_dir, f'{song_name}.gptrlt.txt')
        with open(gptrlt_file, 'w') as rlt_f:
            rlt_f.write(resp)
    elif content_type == "json":
        gptrlt_file = os.path.join(output_dir, f'{song_name}.json')
        with open(gptrlt_file, 'w') as rlt_f:
            try:
                json_content = json.loads(resp)
            except:
                json_content = extract_json(resp)
            json.dump(json_content, rlt_f, ensure_ascii=False)

def get_prompt_from_file(prompt_file):
    prompt = dict()
    # with open(prompt_file, 'r') as f:
    #     data = {}
    #     key = None
    #     value = ''
    #     for line in f:
    #         line = line.strip()
    #         if line.endswith(':'):
    #             if key is not None:
    #                 data[key] = value.strip()
    #             key = line[:-1]
    #             value = ''
    #         else:
    #             value += line
    #     if key is not None:
    #         data[key] = value.strip()

    pattern = r"prefix:\s([\s\S]*)suffix:\s([\s\S]*)"
    with open(prompt_file, "r") as file:
        data = file.read()
    match = re.search(pattern, data)

    prompt["prefix"] = match.group(1)
    prompt["suffix"] = match.group(2)
    return prompt

def get_song_name(song_name):
    '''Avercage_-_Embers =》embers'''
    song_real_name = song_name.split('-')[-1]
    song_real_name = song_real_name.replace('_'," ").strip().lower()
    return song_real_name


if __name__ == "__main__":

    # load config
    config = load_config(config_dict)
    apikey = config.Acess_config.authorization
    model_name = config.Model_config.model_name

    parser = argparse.ArgumentParser(description='use chatgpt ensemble whisper\'s results')
    parser.add_argument('song_name', type=str, help='song name needed to ensemble')
    parser.add_argument('whisper_rlts_dir', type=str, help='dir of whisper rlt')
    parser.add_argument('output_dir', type=str, help='output dir')
    parser.add_argument('--prompt_file', type=str, default='input_prompt.txt', help='prompt you want use')
    parser.add_argument('--sample_num', type=int, default=3, help='num of sampled preditions')
    parser.add_argument('--audio_type', type=str, default="wav", help='type of audio, mp3 or wav')
    parser.add_argument('--content_type', choices=["json",'txt'], help='type of content, json or txt')
    parser.add_argument('--add_language', action='store_true', help='whether to add language info into prompt, if use this param, then it will add')

    args = parser.parse_args()
    song_name = args.song_name
    whisper_rlts_dir = args.whisper_rlts_dir
    output_dir = args.output_dir
    prompt_file = args.prompt_file
    sample_num = args.sample_num
    content_type = args.content_type
    add_language = args.add_language
    audio_type = args.audio_type

    print(song_name)
    prompt = get_prompt_from_file(prompt_file)
    concated_lyrics, num_lyrics, language=ensemble_whisper(song_name, whisper_rlts_dir, sample_num, content_type, audio_type)
    if add_language:
        prompt["prefix"] += f"The language of the input lyrics is: {language}. INPUT:" 

    # assert len(final_prompts) < 4000, "too long prompts" # TODO: this code is wrong, use tiktok cal token nums
    
    # TODO： set this for optinal, for scale up 
    song_name = song_name.replace("/","_")
    prompt_recorded_file = os.path.join(output_dir, f"prompt_final_{song_name}.txt")
    request_msg = get_request_msg(prompt, concated_lyrics, language)
    with open(prompt_recorded_file, 'a') as prompts_f:
        entire_prompt = "\n".join([i['content']for i in request_msg])
        prompts_f.writelines(f'{entire_prompt}\n')
    
    # resp = requests_chatgpt(request_msg, apikey, model_name)

    # save_resp(resp, content_type, output_dir, song_name)
    