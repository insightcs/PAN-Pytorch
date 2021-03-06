# -*- coding: utf-8 -*-
# @Time    : 2018/6/11 15:54
# @Author  : zhoujun
import torch
import shutil
import numpy as np
import os
import cv2
from tqdm import tqdm
from predict import Pytorch_model
from utils import cal_recall_precision_f1, draw_bbox

torch.backends.cudnn.benchmark = True


def main(model_path, img_folder, save_path, gpu_id):
    if os.path.exists(save_path):
        shutil.rmtree(save_path, ignore_errors=True)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_img_folder = os.path.join(save_path, 'img')
    if not os.path.exists(save_img_folder):
        os.makedirs(save_img_folder)
    save_txt_folder = os.path.join(save_path, 'result')
    if not os.path.exists(save_txt_folder):
        os.makedirs(save_txt_folder)
    img_paths = [os.path.join(img_folder, x) for x in os.listdir(img_folder)]
    model = Pytorch_model(model_path, gpu_id=gpu_id)
    total_frame = 0.0
    total_time = 0.0
    for img_path in tqdm(img_paths):
        img_name = os.path.basename(img_path).split('.')[0]
        save_name = os.path.join(save_txt_folder, 'res_' + img_name + '.txt')
        _, boxes_list, t = model.predict(img_path, short_size=640)
        total_frame += 1
        total_time += t
        #img = draw_bbox(img_path, boxes_list, color=(0, 0, 255))
        #cv2.imwrite(os.path.join(save_img_folder, '{}.jpg'.format(img_name)), img)
        file_writer = open(save_name, 'w', encoding='utf-8')
        for box in boxes_list:
            line = ','.join(list(map(str, box))) + '\n'
            file_writer.write(line)
        file_writer.close()
        #np.savetxt(save_name, boxes_list.reshape(-1, 8), delimiter=',', fmt='%d')
    print('fps:{}'.format(total_frame / total_time))
    return save_txt_folder


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = str('0')
    scale = 4
    model_path = 'output_ctw1500_1129/PAN_resnet18_FPEM_FFM/checkpoint/PANNet_epoch_79_hmean_0.8182.pth'
    img_path = '/home/insight/datasets/text_detect/CTW1500/test/images'
    gt_path = '/home/insight/datasets/text_detect/CTW1500/test/gt_labels'
    save_path = 'result'
    gpu_id = 0

    save_path = main(model_path, img_path, save_path, gpu_id=gpu_id)
    result = cal_recall_precision_f1(gt_path=gt_path, result_path=save_path, text_type='curve')
    print(result)
