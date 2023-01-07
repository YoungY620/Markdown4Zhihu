## Please put this file in the same folder of .git/
## This program aims to transfer your markdown file into a way zhihu.com can recognize correctly.
## It will mainly deal with your local images and the formulas inside.


import os, re
import argparse
import subprocess
import chardet
import functools

from PIL import Image
from pathlib2 import Path
from shutil import copyfile

GITEE_REPO_PREFIX = "https://gitee.com/{owner}/{repo}/raw/{branch}/"
GITHUB_REPO_PREFIX = "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
REPO_PREFIX = GITHUB_REPO_PREFIX
COMPRESS_THRESHOLD = 5e5 # The threshold of compression

# The main function for this program
def process_for_zhihu():
    if args.encoding is None:
        with open(str(args.input), 'rb') as f:
            s = f.read()
            chatest = chardet.detect(s)
            args.encoding = chatest['encoding']
        print(chatest)
    with open(str(args.input),"r",encoding=args.encoding) as f:
        lines = f.read()
        lines = image_ops(lines)
        lines = formula_ops(lines)
        lines = table_ops(lines)
        print(lines)
        with open(args.input.parent/(args.input.stem+"(ToPublish).md"), "w+", encoding=args.encoding) as fw:
            fw.write(lines)
        git_ops()

# Deal with the formula and change them into Zhihu original format
def formula_ops(_lines):
    _lines = re.sub('((.*?)\$\$)(\s*)?([\s\S]*?)(\$\$)\n', '\n<img src="https://www.zhihu.com/equation?tex=\\4" alt="\\4" class="ee_img tr_noresize" eeimg="1">\n', _lines)
    _lines = re.sub('(\$)(?!\$)(.*?)(\$)', ' <img src="https://www.zhihu.com/equation?tex=\\2" alt="\\2" class="ee_img tr_noresize" eeimg="1"> ', _lines)
    return _lines

# The support function for image_ops. It will take in a matched object and make sure they are competible
def rename_image_ref(m, original=True):
    # global image_folder_path
    global file_folder_path
    global root
    print("[debug50]", m.group(0), m.group(1), m.group(2), Path(image_folder_path.parent/m.group(1)).is_file(), (original and Path(image_folder_path.parent/m.group(2)).is_file()))
    if not (Path(image_folder_path.parent/m.group(1)).is_file() or (original and Path(image_folder_path.parent/m.group(2)).is_file())):
        return m.group(0)
    given_path = m.group(1) if not original else m.group(2)
    _image_path = file_folder_path.joinpath(given_path).resolve()
    print("[debug53]", _image_path)

    if args.compress:
        img = Image.open(str(_image_path))
        if(img.size[0]>img.size[1] and img.size[0]>1920):
            img=img.resize((1920,int(1920*img.size[1]/img.size[0])),Image.ANTIALIAS)
        elif(img.size[1]>img.size[0] and img.size[1]>1080):
            img=img.resize((int(1080*img.size[0]/img.size[1]),1080),Image.ANTIALIAS)
        _image_path = Path(str(_image_path.parent/(_image_path.stem+"(compressed).jpg")))
        img.convert('RGB').save(str(_image_path), optimize=True,quality=85)
    if _image_path.suffix != ".jpg":
        img = Image.open(str(_image_path))
        _image_path = Path(str(_image_path.parent)+ _image_path.stem + ".jpg")
        img.convert('RGB').save(str(_image_path), optimize=True,quality=85)

    if original:
        return "!["+m.group(1)+"]("+REPO_PREFIX+str(_image_path.relative_to(root))+")"
    else:
        return '<img src="'+REPO_PREFIX+str(_image_path.relative_to(root))+'"'

# Search for the image links which appear in the markdown file. It can handle two types: ![]() and <img src="LINK" alt="CAPTION" style="zoom:40%;" />.
# The second type is mainly for those images which have been zoomed.
def image_ops(_lines):
    # if args.compress:
    #     _lines = re.sub(r"\!\[(.*?)\]\((.*?)\)",lambda m: "!["+m.group(1)+"]("+REPO_PREFIX+str(image_folder_path.name)+"/"+Path(m.group(2)).stem+".jpg)", _lines)
    #     _lines = re.sub(r'<img src="(.*?)"',lambda m:'<img src="'+REPO_PREFIX+str(image_folder_path.name)+"/"+Path(m.group(1)).stem+'.jpg"', _lines)
    # else:
    _lines = re.sub(r"\!\[(.*?)\]\((.*?)\)",functools.partial(rename_image_ref, original=True), _lines)
    # _lines = re.sub(r'<img src="(.*?)"',functools.partial(rename_image_ref, original=False), _lines)
    return _lines

# Deal with table. Just add a extra \n to each original table line
def table_ops(_lines):
    return re.sub("\|\n",r"|\n\n", _lines)

# Reduce image size and compress. It the image is bigger than threshold, then resize, compress, and change it to jpg.
def reduce_image_size(old_folder):
    image_folder_new_path = args.input.parent/(args.input.stem+"_compressed")
    if not os.path.exists(str(image_folder_new_path)): 
        os.mkdir(str(image_folder_new_path))
    for image_path in [i for i in list(old_folder.iterdir()) if not i.name.startswith(".") and i.is_file()]:
        print(image_path)
        if os.path.getsize(image_path)>COMPRESS_THRESHOLD:
            img = Image.open(str(image_path))
            if(img.size[0]>img.size[1] and img.size[0]>1920):
                img=img.resize((1920,int(1920*img.size[1]/img.size[0])),Image.ANTIALIAS)
            elif(img.size[1]>img.size[0] and img.size[1]>1080):
                img=img.resize((int(1080*img.size[0]/img.size[1]),1080),Image.ANTIALIAS)
            img.convert('RGB').save(str(image_folder_new_path/(image_path.stem+".jpg")), optimize=True,quality=85)
        else:
            copyfile(image_path, str(image_folder_new_path/image_path.name))
    return image_folder_new_path

# Push your new change to github remote end
def git_ops():
    subprocess.run(["git","add","-A"])
    subprocess.run(["git","commit","-m", "update file "+args.input.stem])
    subprocess.run(["git","push", "-f -u" if args.forcepush else "-u", args.remote, args.branch])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--compress', action='store_true', help='Compress the image which is too large')
    parser.add_argument('-i', '--input', type=str, help='Path to the file you want to transfer.')
    parser.add_argument("--images", type=str, default="./assets", help="Path to images related to the repo.")
    parser.add_argument('-e', '--encoding', type=str, help='Encoding of the input file')
    parser.add_argument("--platform", type=str, default="github", choices=["github", "gitee"], help="Git platform. Default to \"github\"")
    parser.add_argument("--owner", type=str, required=True, help="The name of org or user owning the repo.")
    parser.add_argument("--repo", type=str, required=True, help="The name of repo.")
    parser.add_argument("--branch", type=str, default="master", help="The branch you want to push to. Default to \"master\"")
    parser.add_argument("--remote", type=str, default="origin", help="The name of origin. Default to \"origin\"")
    parser.add_argument("--forcepush", action="store_true", help="Add \"-f\" when push the repo.")
    
    args = parser.parse_args()
    if args.input is None:
        raise FileNotFoundError("Please input the file's path to start!")

    if args.platform == None or args.platform == "github":
        REPO_PREFIX = GITHUB_REPO_PREFIX.format(owner=args.owner, repo=args.repo, branch=args.branch)
    elif args.platform == "gitee":
        REPO_PREFIX = GITEE_REPO_PREFIX.format(owner=args.owner, repo=args.repo, branch=args.branch)
    else:
        raise NotImplementedError

    args.input = Path(args.input)
    file_folder_path = args.input.parent/(args.input.stem)
    root = os.path.dirname(os.path.abspath(__file__))
    args.images = os.path.join(root, args.images)
    args.images = os.path.relpath(args.images, root)
    image_folder_path = Path(args.images)
    process_for_zhihu()
