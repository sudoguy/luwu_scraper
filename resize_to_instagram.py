from tqdm import tqdm
from PIL import Image
import os
from multiprocessing import Pool


def filter_with_photo(dirs):
    return [my_dir for my_dir in dirs if [d for d in os.listdir(my_dir) if '.jpg' in d]]


def change_photo(path):
    im = Image.open(path + '/photo.jpg')
    old_size = im.size

    new_size = (max(im.size), max(im.size))
    new_im = Image.new("RGB", new_size, 'white')

    new_im.paste(im, ((new_size[0] - old_size[0]) // 2, (new_size[1] - old_size[1]) // 2))
    new_im.save(path + '/photo.jpg', 'JPEG')


if __name__ == '__main__':
    path = 'products/'
    dirs = [f'{path}{d}' for d in os.listdir(path) if os.path.isdir(f'{path}{d}')]
    dirs = filter_with_photo(dirs)

    pool = Pool()
    for _ in tqdm(pool.imap_unordered(change_photo, dirs), total=len(dirs)):
        pass
    pool.close()
    pool.join()
