import argparse
import flickrapi
import json
import glob
import sys
import zipfile
from PIL import Image, ImageFont, ImageDraw, ExifTags
from settings import flickr_key, flickr_secret, flickr_username

FONT_PATH = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'


def final_processing(img_path, title, date):
    """Add title and date to a photo. If necessary,
    rotate the photo as well.
    """
    try:
        img_fraction = 0.02
        img = Image.open(img_path)

        # rotate the picture if needed
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        e = img._getexif()
        if e:
            exif = dict(e.items())
            if exif:
                try:
                    orient = exif[orientation]
                    if orient == 3:
                        img = img.transpose(Image.ROTATE_180)
                    elif orient == 6:
                        img = img.transpose(Image.ROTATE_270)
                    elif orient == 8:
                        img = img.transpose(Image.ROTATE_90)
                except:
                    pass

        # add the title and the date and save. put it in a try/except
        # deal with "image truncated" errors from PIL
        draw = ImageDraw.Draw(img)
        font_size = 32
        font = ImageFont.truetype(FONT_PATH, font_size)

        while font.getsize(title)[1] < img_fraction * img.size[1]:
            font_size += 2
            font = ImageFont.truetype(FONT_PATH, font_size)

        margin = font.getsize(title)[1]
        line_2 = (margin * 1.5) + font.getsize(title)[1]

        # border
        draw.text((margin-2, margin-2), title, font=font, fill='black')
        draw.text((margin+2, margin-2), title, font=font, fill='black')
        draw.text((margin-2, margin+2), title, font=font, fill='black')
        draw.text((margin+2, margin+2), title, font=font, fill='black')

        draw.text((margin-2, line_2-2), date, font=font, fill='black')
        draw.text((margin+2, line_2-2), date, font=font, fill='black')
        draw.text((margin-2, line_2+2), date, font=font, fill='black')
        draw.text((margin+2, line_2+2), date, font=font, fill='black')

        # fill
        draw.text((margin, margin), title, font=font, fill='white')
        draw.text((margin, line_2), date, font=font, fill='white')

        # save
        img.save(img_path, quality=95)
        return True
    except:
        return False


def extract_zip(zip, destination_path):
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(destination_path)


def flickr_setup(destination_path, photoset):
    flickr = flickrapi.FlickrAPI(flickr_key, flickr_secret)
    info = flickr.people.findByUsername(username=flickr_username, format='json')
    info = json.loads(info.decode('utf-8'))
    user_id = info['user']['nsid']
    info = flickr.people.getInfo(user_id=user_id, format='json')
    info = json.loads(info.decode('utf-8'))
    info = flickr.photosets.getPhotos(user_id=user_id, photoset_id=photoset, extras='date_taken', format='json')
    info = json.loads(info.decode('utf-8'))
    photo_list = info['photoset']['photo']

    sorted_list = sorted(photo_list, key=lambda entry: entry['datetaken'])

    for entry in sorted_list:
        glob_path = '{0}/*{1}*'.format(destination_path, entry['id'])
        pic_path = glob.glob(glob_path)
        if len(pic_path) != 1:
            print('BAD!!!! %s' % glob_path)
            print(pic_path)
            sys.exit(1)
        print('%s %s' % (entry['title'], entry['datetaken'].split()[0]))
    return sorted_list


parser = argparse.ArgumentParser()
parser.add_argument("--zip", help="full path to the zip file")
parser.add_argument("--slides", help="full path to the slides directory")
parser.add_argument("--name", help="name of the slides sub-directory")
parser.add_argument("--photoset", help="ID of the flickr photoset")
args = parser.parse_args()

destination_path = '{0}/{1}'.format(args.slides, args.name)
extract_zip(args.zip, destination_path)
sorted_list = flickr_setup(destination_path, args.photoset)
for entry in sorted_list:
    glob_path = '{0}/*{1}*'.format(destination_path, entry['id'])
    pic_path = glob.glob(glob_path)
    print('%s %s' % (entry['title'], entry['datetaken'].split()[0]))
    final_processing(pic_path[0], entry['title'], entry['datetaken'].split()[0])
