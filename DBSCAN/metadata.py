# from exif import Image
from PIL import Image
from PIL import ExifTags


class metadata(object):
    def __init__(self, image):
        self.image = Image.open(image)

        exifData = {}
        exifDataRaw = self.image._getexif()
        for tag, value in exifDataRaw.items():
            decodedTag = ExifTags.TAGS.get(tag, tag)
            exifData[decodedTag] = value
