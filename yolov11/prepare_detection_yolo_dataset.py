import json
import random
import shutil
from glob import glob
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm


def bbox_ls_to_yolo(x: float, y: float, width: float, height: float) -> tuple:
    x = (x + width / 2) / 100
    y = (y + height / 2) / 100
    w = width / 100
    h = height / 100
    return x, y, w, h


def create_label_files(task, labels_dest, label_by, names):
    label_file_dest = f'{labels_dest}/{Path(task["image"]).stem}.txt'
    lines = []
    if not task.get('rect-1'):
        return
    label_by_res = task[label_by]
    if not isinstance(label_by_res, list):
        label_by_res = [label_by_res]
    for bbox, _c in zip(task['rect-1'], label_by_res):
        yolo_bbox = bbox_ls_to_yolo(bbox['x'], bbox['y'], bbox['width'],
                                    bbox['height'])
        lines.append([str(names[_c]), *[str(x) for x in yolo_bbox]])

    lines = '\n'.join([' '.join(x) for x in lines])
    with open(label_file_dest, 'w') as f:
        f.writelines(lines)


def split_data(output_dir: str,
               images_source_dir='ls_images',
               labels_source_dir='ls_labels',
               seed: int = 8) -> None:
    random.seed(seed)

    imgs_full = glob(f'{output_dir}/{images_source_dir}/*')
    imgs = [Path(x).stem for x in imgs_full]
    labels_full = glob(f'{output_dir}/{labels_source_dir}/*')
    labels = [Path(x).stem for x in labels_full]

    in_imgs_but_not_in_labels = [x for x in imgs if x not in labels]
    in_labels_but_not_in_images = [x for x in labels if x not in imgs]

    imgs_to_delete = [
        x for x in imgs_full if Path(x).stem in in_imgs_but_not_in_labels
    ]
    labels_to_delete = [
        x for x in labels_full if Path(x).stem in in_labels_but_not_in_images
    ]

    for item in imgs_to_delete + labels_to_delete:
        Path(item).unlink()

    for subdir in ['images/train', 'labels/train', 'images/val', 'labels/val']:
        Path(f'{output_dir}/{subdir}').mkdir(parents=True, exist_ok=True)

    images = sorted(glob(f'{output_dir}/{images_source_dir}/*'))
    labels = sorted(glob(f'{output_dir}/{labels_source_dir}/*'))
    pairs = list(zip(images, labels))

    train_len = round(len(pairs) * 0.8)
    random.shuffle(pairs)

    train, val = pairs[:train_len], pairs[train_len:]

    for im, label in tqdm(train):
        shutil.copy(im, f'{output_dir}/images/train')
        shutil.copy(label, f'{output_dir}/labels/train')

    for im, label in tqdm(val):
        shutil.copy(im, f'{output_dir}/images/val')
        shutil.copy(label, f'{output_dir}/labels/val')

    shutil.rmtree(f'{output_dir}/{images_source_dir}', ignore_errors=True)
    shutil.rmtree(f'{output_dir}/{labels_source_dir}', ignore_errors=True)


def run(project_exported_file, label_by):  # JSON-MIN

    images_source_dir = 'ls_images'
    labels_source_dir = 'ls_labels'

    project_folder = Path(project_exported_file).stem
    Path(f'{project_folder}/{images_source_dir}').mkdir(exist_ok=True,
                                                        parents=True)
    Path(f'{project_folder}/{labels_source_dir}').mkdir(exist_ok=True)

    with open(project_exported_file) as j:
        data = json.load(j)

    names = ['Background']
    for x in data:
        if x.get('is_background') == 'Background':
            continue
        try:
            names.append(sum([x['rectanglelabels'] for x in x['label']], []))
        except KeyError:
            continue

    names = [
        item for sublist in names
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]
    names = list(set(names))
    names = {k: v for k, v in zip(sorted(list(set(names))), range(len(names)))}

    notexist_images = []

    for task in tqdm(data):
        if 'RECNX' in task['image']:
            file_name = '/'.join(Path(task['image']).parts[-3:])
        else:
            file_name = '/'.join(Path(task['image']).parts[-2:])
        local_image_path = Path(f'{data_folder}/{file_name}')

        if not Path(local_image_path).exists():
            if 'RECNX' not in task['image']:
                notexist_images.append(local_image_path)
            continue

        output_image_path = Path(
            f'{project_folder}/{images_source_dir}/{local_image_path.name}')

        shutil.copy(local_image_path, output_image_path)

    labels_dest = f'{project_folder}/{labels_source_dir}'
    for task in tqdm(data):
        create_label_files(task, labels_dest, label_by, names)

    split_data(project_folder)


def main():
    """
    Main function to prepare the detection dataset.
    """
    load_dotenv()
    args = opts()
    run(project_exported_file=args.project_exported_file,
        label_by=args.label_by)


if __name__ == '__main__':
    main()
