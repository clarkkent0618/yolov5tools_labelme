import os
import json
import argparse
from tqdm import tqdm
import shutil

'''
lablme的标签不是标号，是label名称，可能存在拼写错误
'''
def checkClassNameTypo(label_folder, labels):
    # print(label_folder)
    label_names = set()
    json_files = os.listdir(label_folder)
    # print(json_files)
    for json_file in json_files:
        with open(os.path.join(label_folder, json_file), 'r') as json_f:
            labelme_json = json.load(json_f)
            json_f.close
        shapes = labelme_json['shapes']
        for shape in shapes:
            shape_type = shape['shape_type']
            if shape_type != 'rectangle':
                continue
            else:
                label = shape['label']
                if label=='soket':
                    label = 'socket'
                if label=='duastpan':
                    label = 'dustpan'
                label_names.add(str(label))
    # return list(label_names) if list(label_names).sort()==labels.sort() else 'No typo'
    return list(label_names)

def modifyClassNameTypo():
    pass

def onefolder(label_folder, labels:list, root_dict):
    print(f'{label_folder}...')
    json_files = os.listdir(label_folder)
    image_nums = len(json_files)
    print(image_nums)
    for i, json_file in enumerate(tqdm(json_files)):
        with open(os.path.join(label_folder, json_file), 'r') as json_f:
            labelme_json = json.load(json_f)
            json_f.close
        
        shapes = labelme_json['shapes']
        image_path = labelme_json['imagePath']
        image_height = labelme_json['imageHeight']
        image_width = labelme_json['imageWidth']
        if(i < 0.9 * image_nums):
            open(os.path.join(root_dict, 'train/labels', image_path[:-4]) + '.txt', 'w').write('')
        else:
            open(os.path.join(root_dict, 'valid/labels', image_path[:-4]) + '.txt', 'w').write('')


        for shape in shapes:
            shape_type = shape['shape_type']
            if shape_type != 'rectangle':
                continue
            else:
                label = str(shape['label'])
                points = shape['points'] # [[topleft.x, topleft.y], [bottomright.x, bottomright.y]]
                if label in labels:
                    cls_idx = labels.index(label)
                else:
                    continue
                x_center = (points[1][0] + points[0][0]) / 2 / image_width
                y_center = (points[1][1] + points[0][1]) / 2 / image_height
                width = (points[1][0] - points[0][0]) / image_width
                height = (points[1][1] - points[0][1]) / image_height
                if i < image_nums * 0.9: # train data
                    shutil.copyfile(os.path.join('/home/ubuntu/yolov5_datasets/indoor/images', image_path),
                                    os.path.join(root_dict, 'train/images', image_path))
                    with open(os.path.join(root_dict, 'train/labels', image_path[:-4]) + '.txt', 'a') as train_f:
                        train_f.write(f"{cls_idx} {x_center} {y_center} {width} {height}\n")
                else: # test data
                    shutil.copyfile(os.path.join('/home/ubuntu/yolov5_datasets/indoor/images', image_path),
                                    os.path.join(root_dict, 'valid/images', image_path))
                    with open(os.path.join(root_dict, 'valid/labels', image_path[:-4]) + '.txt', 'a') as test_f:
                        test_f.write(f"{cls_idx} {x_center} {y_center} {width} {height}\n")


if __name__ == '__main__':
    labels = ['PC case', 'broom', 'dustpan', 'bookshelf', 'pillow',
              'printer', 'elevator', 'socket', 'painting']
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--check-classname', action='store_true', default=False, help='whether to check classname typos'
    )
    parser.add_argument(
        '--label-folder', type=str, default='', help='the dict of the folder of labelme json files'
    )
    parser.add_argument(
        '--root-dict', type=str, default='', help='where to create the dataset'
    )
    parser.add_argument(
        '--image-folder', type=str, default='', help='where the original image were saved'
    )
    args = parser.parse_args(args=['--root-dict', '/home/ubuntu/yolov5_datasets/indoor',
                                   '--label-folder', '/home/ubuntu/yolov5_datasets/labels',
                                   '--image-folder', ''])
    folder_names =  os.listdir(args.label_folder)
    if args.check_classname:
        for folder_name in folder_names:
            if folder_name == '地面_墙壁_玻璃_label':
                continue
            else:
                result = checkClassNameTypo(os.path.join(args.label_folder, folder_name), labels)
                print(result)
    else:
        for folder_name in folder_names:
            if folder_name == '地面_墙壁_玻璃_label':
                continue
            else:
                onefolder(os.path.join(args.label_folder, folder_name), labels, args.root_dict)
