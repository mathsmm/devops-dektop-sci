from displayable_path import DisplayablePath
from pathlib import Path
import time

def all_files_to_dict(base_folder: str, exclusions: list):
    def is_not_hidden(path):
        # return not path.name.startswith(".svn")
        for ex in exclusions:
            if path.name.lower().find(ex.lower()) != -1:
                return False
        return True

    paths = DisplayablePath.make_tree(Path(base_folder), criteria=is_not_hidden)
    dict_files = {}
    for path in paths:
    #     print(path.displayable())
        pair = path.generate_key_value_path()
        if pair is not None:
            dict_files.update(pair)

    # for k, v in dict_files.items():
    #     print(k, v)

    return dict_files

def main():
    d = all_files_to_dict('C:\\DW\\Practice', ['.svn','.db','.jpg'])
    for k, v in d.items():
        time.sleep(0.02)
        print(k, v)

if __name__=="__main__":
    main()