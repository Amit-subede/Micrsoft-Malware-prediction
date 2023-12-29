from tqdm import tqdm
import imageio
import os
import codecs
import array
import numpy as np
def collect_img_asm():
    for i , asmfile in tqdm(enumerate(os.listdir("asmFiles"))):
        filename = asmfile.split('.')[0]
        file = codecs.open("asmFiles/" + asmfile, 'rb')
        filelen = os.path.getsize("asmFiles/" + asmfile)
        width = int(filelen ** 0.5)
        rem = int(filelen / width)
        arr = array.array('B')
        arr.frombytes(file.read())
        file.close()
        reshaped = np.reshape(arr[:width * width], (width, width))
        reshaped = np.uint8(reshaped)
        os.remove("asmFiles/" + asmfile)
        imageio.imwrite('asmFiles/' + filename + '.png',reshaped)
collect_img_asm()