#!/usr/bin/python3
import sys
from pathlib import Path

def main():
    print("starting...")
    if (args_count := len(sys.argv)) == 2:
        if sys.argv[1] == "help":
            print("convert.py /PATH_TO_CHERRYTREE_DB/ /PATH_TO_NEW_DIR/")
            raise SystemExit(0)
    elif args_count > 3:
        print("Too many args: type 'help' for usage")
        raise SystemExit(2)
    elif args_count < 3:
        print("Too few args: type 'help' for usage")
        raise SystemExit(2)

    ct_file = Path(sys.argv[1])
    target_dir = Path(sys.argv[2])
    
    print(f'ct_file:{ct_file} target_dir:{target_dir}')

    if target_dir.is_dir():
        print("The target directory exists already! this program will not overwrite! exiting...")
        raise SystemExit(1)

    #TODO open connection to the cherrytree file and attempt to read nodes

    target_dir.mkdir()
    print('finished')

if __name__ == "__main__":
    main()
