# cherrytree2markdown

This program converts a CherryTree ".ctb" sqlite db into a directory of markdown files organized into folders.

Currently the "flavor" of markdown is targeted for Obsidian but more may be added in the future if requested.

## Set Up and Run

Until, I setup a github release with a exe/bin, you must follow these steps to use this program.

Built with **Python 3.12**

### Windows

Make sure Python 3.12 is installed via python.org

```powershell
git clone https://github.com/ChaseClark/cherrytree2markdown.git
cd cherrytree2markdown
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\convert.py PATH_TO_YOUR_CHERRYTREE_DB
```

Check the generated "c2md_gen" folder for output

### Ubuntu

Make sure Python 3.12 is installed via deadsnakes or whatever

```bash
git clone https://github.com/ChaseClark/cherrytree2markdown.git
cd cherrytree2markdown
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3.12 src/convert.py PATH_TO_YOUR_CHERRYTREE_DB
```

Check the generated "c2md_gen" folder for output

## Make Executable for your OS

This should work for most operating systems.

```bash
pyinstaller src/convert.py -F
```

Check "dist" folder for output.

Read error logs for missing dependencies you may have.

## Warning

This project deletes the "c2md_gen" folder if you rerun it.

## Contributing

Issues and PRs are always welcome.

If you have issue, please attach sample .ctb file so I can test.

## Todo

- [ ] Add flag for changing where the output is generated
- [ ] Add flag for --noconfirm/-y, to skip the overwrite message
- [ ] Set up github actions for at least a Windows .exe
- [ ] Make simple GUI with file picker
