import torch
import torchvision
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt

from torch.utils.data import Dataset
from PIL import Image, ImageDraw
from pathlib import PurePath

class CelebADataset(Dataset):

    def __init__(self, root, image_size, split, transform):
        self.root = root
        self.image_size = image_size
        self.split = split
        self.split_code_map = {
            "train": "0",
            "eval": "1",
            "test": "2"
        }
        self.file_list = self.read_file_list()
        self.transform = transform

    
    def __len__(self):
        return len(self.file_list)

    
    def __getitem__(self, idx):
        filename = self.file_list[idx]
        with open(filename, 'rb') as f:
            og_image = Image.open(f)
            og_image = og_image.convert('RGB')
            og_image = og_image.resize(self.image_size)
            # TODO: normalize

            mask = Image.new("L", og_image.size, 255)
            draw = ImageDraw.Draw(mask)
            draw.rectangle((22, 22, 44, 44), fill=0)
            # mask.save('mask_rec.jpg', quality=95)

            target_image = Image.new("RGB", og_image.size)
            target_image.paste(og_image, (0, 0), mask)
            # target_image.save('target_image.jpg', quality=95)

            if self.transform:
                og_image = self.transform(og_image)
                target_image = self.transform(target_image)
            mask = torch.FloatTensor(np.array(mask))

            return og_image, target_image, mask
    

    def read_file_list(self):
        root_path = PurePath(self.root)
        eval_file = root_path.joinpath("list_eval_partition.txt")
        file_list = list()
        with open(eval_file, 'r') as f:
            line = f.readline()
            while line:
                space_split = line.strip().split(" ")
                # print(space_split)
                if self.split_code_map[self.split] == space_split[1]:
                    filename = space_split[0].split(".")[0]
                    filename = filename + ".png"
                    file_list.append(str(root_path.joinpath("img_align_celeba_png", filename)))
                line = f.readline()
        return file_list

def get_celeba_data():
    transform=torchvision.transforms.Compose([
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    dset = CelebADataset("/home/ssing57/dataset", (64, 64), "train", transform)
    train_dataloader = torch.utils.data.DataLoader(dset, batch_size=64, shuffle=True)
    return train_dataloader

if __name__ == "__main__":
    train_dataloader = get_celeba_data()
    # # Decide which device we want to run on
    # # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    device = "cpu"

    # # Plot some training images
    real_batch = next(iter(train_dataloader))
    plt.figure(figsize=(8,8))
    plt.axis("off")
    plt.title("Training Images")
    print(torchvision.utils.make_grid(real_batch[1].to(device)[:64], padding=2, normalize=True).cpu().shape)
    a = np.transpose(torchvision.utils.make_grid(real_batch[1].to(device)[:64], padding=2, normalize=True).cpu(),(1,2,0)).numpy()
    # print(a)
    im = Image.fromarray((a * 255).astype(np.uint8))
    im.save("file.jpeg")
    # plt.savefig()
