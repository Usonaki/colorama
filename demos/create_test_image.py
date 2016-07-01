# (C) Copyright 2016, Christian Burri
from PIL import Image
from os.path import join, dirname
from colorsys import hls_to_rgb
import fixpath


def linspace(points, start=0, end=1, endpoint=True):
    rg = points
    if endpoint:
        points -= 1
    for i in range(rg):
        yield (end - start) / points * i + start


def create_test_image(block_width=7, block_height=4, h_blocks=4, v_blocks=6, as_string=True):
    width, height = block_width * h_blocks, block_height * v_blocks
    block_count = h_blocks * v_blocks
    hue_values = [*linspace(block_count, endpoint=False)]
    light_values = [*linspace(block_width + 2)][1:-1]  # remove first and last item
    sat_values = [*linspace(block_height, 1, 0, endpoint=False)]
    img_string = b''
    img_list = []
    for j in range(v_blocks):
        for l in range(block_height):
            sat = sat_values[l]
            for i in range(h_blocks):
                hue = hue_values[j * h_blocks + i]
                for k in range(block_width):
                    light = light_values[k]
                    rgb = hls_to_rgb(hue, light, sat)
                    r, g, b = round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255)
                    img_list.append((r, g, b))
                    img_string += bytes([r])  # red
                    img_string += bytes([g])  # green
                    img_string += bytes([b])  # blue
    for j in range(block_height):
        for i in range(width):
            rgb = hls_to_rgb(0, i / (width - 1), 0)
            light = round(rgb[0] * 255)
            img_list.append((light, light, light))
            img_string += bytes([light]) * 3
    if as_string:
        return img_string, width, height+block_height
    return img_list, width, height+block_height


def channel_test(channel, block_width=79, block_height=79, as_string=True):
    width, height = block_width, block_height
    hue = {'red': 0, 'green': 1 / 3, 'blue': 2 / 3}[channel]
    light_values = [*linspace(block_width + 2)][1:-1]  # remove first and last item
    sat_values = [*linspace(block_height, 1, 0, endpoint=False)]
    img_string = b''
    img_list = []
    for l in range(block_height):
        sat = sat_values[l]
        for k in range(block_width):
            light = light_values[k]
            rgb = hls_to_rgb(hue, light, sat)
            r, g, b = round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255)
            img_list.append((r, g, b))
            img_string += bytes([r])  # red
            img_string += bytes([g])  # green
            img_string += bytes([b])  # blue
    if as_string:
        return img_string, width, height
    return img_list, width, height


if __name__ == "__main__":
    img_string, width, height = create_test_image()
    img = Image.frombytes('RGB', (width, height), img_string)
    img_file = join(dirname(__file__), 'test_image.png')
    img.save(img_file)

    img_string, width, height = channel_test('red')
    img = Image.frombytes('RGB', (width, height), img_string)
    img_file = join(dirname(__file__), 'test_red.png')
    img.save(img_file)

    img_string, width, height = channel_test('green')
    img = Image.frombytes('RGB', (width, height), img_string)
    img_file = join(dirname(__file__), 'test_green.png')
    img.save(img_file)

    img_string, width, height = channel_test('blue')
    img = Image.frombytes('RGB', (width, height), img_string)
    img_file = join(dirname(__file__), 'test_blue.png')
    img.save(img_file)
