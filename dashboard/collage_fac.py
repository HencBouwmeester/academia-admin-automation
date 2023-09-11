import math
import os
import matplotlib.pyplot as plt

import requests

WIDTH = 400
HEIGHT = 400

# Config:
images_dir = './qrcodes'
result_grid_filename = './grid.png'
result_figsize_resolution = 40 # 1 = 100px

"""
names = {
    "Aubree Freeman": "afreem21",
    "Ben Dyhr": "bdyhr",
    "Brendan Fry": "bfry2",
    "Brooke Evans": "bevans21",
    "David Ruch": "ruch",
    "Diane Davis": "ddavi102",
    "Don Gilmore": "gilmored",
    "Chris Harder": "harderc",
    "Shelley Poole": "srohde2",
    "Eliza Moore": "emoore32",
    "Erika Lynn": "elynn1",
    "Henc Bouwmeester": "hbouwmee",
    "Honor Heer": "hheer",
    "Jessica Bertram": "jbertra3",
    "John Carter": "jcarte11",
    "John Ethier": "jethier",
    "Jon Schauble": "jschaub1",
    "Kellie Zolnikov": "kzolniko",
    "Leah Butler": "lbutle14",
    "Linda Sundbye": "sundbyel",
    "Mark Koester": "koesterm",
    "Mona Mocanasu": "mmocanas",
    "Nels Grevstad": "ngrevsta",
    "Patricia McKenna": "mckennap",
    "Qin Yang": "qyang1",
    "Rob Niemeyer": "niemeye1",
    "Shahar Boneh": "bonehs",
    # "Yanxi Li": "yli7",
}

for name in names:
    DATA = "https://webapp.msudenver.edu/directory/profile.php?uName="+names[name]

    image = requests.get(f"https://chart.googleapis.com/chart?chs={WIDTH}x{HEIGHT}&cht=qr&chl={DATA}")
    image.raise_for_status()

    filename = images_dir + "/" + names[name] + "_qr.jpg"
    print("Creating QR code for " + name)
    with open(filename, "wb") as qr:
        qr.write(image.content)

"""

images_list = os.listdir(images_dir)
images_count = len(images_list)
print('Images: ', images_list)
print('Images count: ', images_count)

# Calculate the grid size:
grid_size = math.ceil(math.sqrt(images_count))

# Create plt plot:
fig, axes = plt.subplots(grid_size, grid_size, figsize=(result_figsize_resolution, result_figsize_resolution+25))

current_file_number = 0
for image_filename in images_list:
    x_position = current_file_number % grid_size
    y_position = current_file_number // grid_size

    print(images_dir + '/' + images_list[current_file_number])
    plt_image = plt.imread(images_dir + '/' + images_list[current_file_number])
    axes[x_position, y_position].imshow(plt_image)
    axes[x_position, y_position].spines[['left', 'bottom', 'right', 'top']].set_visible(False)
    # plt.gca().axison = False
    axes[x_position, y_position].tick_params(axis='x', colors='white')
    axes[x_position, y_position].tick_params(axis='y', colors='white')
    name = image_filename.split('_')[0]
    axes[x_position, y_position].set_title(name+"@msudenver.edu", fontsize = 24)
    axes[x_position, y_position].set_xlabel("Scan for\nOffice Hours", fontsize = 40)
    print((current_file_number + 1), '/', images_count, ': ', image_filename)

    current_file_number += 1

plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
plt.savefig(result_grid_filename)
