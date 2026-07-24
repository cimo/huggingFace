# HuggingFace
Tool for managing models on Hugging Face.

## Usage
1. In "src/upload.py" change with your hugging face username:
```
self.author = "xxx"
```

2. Create a folder inside the model directory with the exact name of your branch and place the model file in that folder.

3. Write on terminal:
```
python3 src/upload.py
```

4. Insert the hugging face token in the terminal and the script will upload the file.<br>
Works similarly to git, only modified files are uploaded (but more fast than git).
