
import sys
import torch
import re
import kaldiio
import json
import os
# use our espnet module
sys.path.insert(0, '/home/nlp/ASR/espnet')
from espnet.nets.beam_search import BeamSearch



def recog(wav_path):
    target_path = '/home/nlp/ASR/espnet/egs/FSW/single_wav/inference.wav'

    if os.path.isfile(target_path):
        print('remove old inference.wav')
        os.remove(target_path)
    print('change sample rate to 16k......')
    print(os.system('ffmpeg -i {} -ar 16000 {}'.format(wav_path,target_path)))
    print(os.system('cd /home/nlp/ASR/espnet/egs/FSW/ ; sh /home/nlp/ASR/espnet/egs/FSW/recog.sh'))

    json_path  = '/home/nlp/Demo/api/asr_result/inference/result.json'
    with open(json_path, "r") as f:
        result = json.load(f)
    print(result)
    text = result['utts']['inference']['output'][0]['rec_text']
    text = text.replace('<eos>','')
    return text







def wav2fbank(wav_path, language='Chinese'):
    # copy wav to target folder

    # wav_path = '/home/nlp/Demo/api/wav/test1.wav'
    target_path = '/home/nlp/ASR/espnet/egs/FSW/single_wav/inference.wav'

    if os.path.isfile(target_path):
        print('remove old inference.wav')
        os.remove(target_path)

    print('change sample rate to 16k......')
    print(os.system('ffmpeg -i {} -ar 16000 {}'.format(wav_path,target_path)))

    if language == 'Chinese':
        print('get fbank  chinese.........')
        print(os.system('cd /home/nlp/ASR/espnet/egs/FSW/ ; sh /home/nlp/ASR/espnet/egs/FSW/get_fbank_cn.sh'))
    elif language == 'Taiwanese':
        print('get fbank taiwanese .........')
        print(os.system('cd /home/nlp/ASR/espnet/egs/FSW/ ; sh /home/nlp/ASR/espnet/egs/FSW/get_fbank_tw.sh'))
    else:
        print('language error')
        

    fp = open('/home/nlp/ASR/espnet/egs/FSW/single_wav/fbank/dump/feats.1.scp','r')
    line = fp.readline()
    fbank_path = line.split()[1].replace('\n','')
    print(fbank_path)
    fp.close()


    return fbank_path




def asr(model_dir= "/home/nlp/ASR/espnet/egs/aishell/asr1/exp/train_nodev_pytorch_conformer_train/results", 
fbank_path='/home/nlp/ASR/espnet/egs/FSW/single_wav/fbank/raw_fbank_single_wav.1.ark:10' , 
beam_size=2 , 
decoder_weight = 0.5 , 
ctc_weight = 0.5,
language = 'Chinese'):
    
    # for chinese asr model
    if language == 'Chinese':
        from espnet.nets.pytorch_backend.e2e_asr_conformer_self_mix import E2E
        # model_dir= "/home/nlp/ASR/espnet/egs/aishell/asr1/exp/train_nodev_pytorch_train_pytorch_conformer/results"
        model_dir = '/home/nlp/ASR/espnet/egs/GrandChallenge/exp/train_pytorch_conformer_self_mix_train/results'
    elif language == 'Taiwanese':
    # for taiwanese asr model
        from espnet.nets.pytorch_backend.e2e_asr_conformer_self_mix import E2E
        model_dir = '/home/nlp/ASR/espnet/egs/FSW/exp/train_nodev_pytorch_conformer_self_mix_train/results'

    # load model
    with open(model_dir + "/model.json", "r") as f:
        idim, odim, conf = json.load(f)
    model = E2E.build(idim, odim, **conf)
    ckpt = torch.load(model_dir + "/model.loss.best" , map_location='cpu')
    model.load_state_dict(ckpt)


    model.cpu().eval()
    vocab = conf["char_list"]

    fbank = kaldiio.load_mat(fbank_path)

    weights = dict(
        decoder=0.5,
        ctc=0.5,
        lm=0.7,
        ngram=0.3,
        length_bonus=0.0,
    )

    # setup beam search
    bs = BeamSearch(
        scorers=model.scorers(), 
        # weights={"decoder": decoder_weight, "ctc": ctc_weight},
        weights=weights,
        sos=model.sos, 
        eos=model.eos,
        beam_size=beam_size, 
        vocab_size=len(vocab))


    # GPU decoding: model.cuda(), bs.cuda()
    with torch.no_grad():
        encoded = model.encode(torch.as_tensor(fbank))
        result = bs(encoded)  # get N-best results

    print("N-best list:")
    texts = []
    from opencc import OpenCC
    cc = OpenCC('s2twp')
    for n, hyp in enumerate(result, 1):
        text = "".join(vocab[y] for y in hyp.yseq).replace("<space>", " ").replace("<eos>", "")
        scores = {k: f"{float(v):0.3f}" for k, v in hyp.scores.items()}
        print(f"{n}: {text}, score: {scores},len:{len(text)}")
        texts.append(cc.convert(text))
    return texts



