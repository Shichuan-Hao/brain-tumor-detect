
```
conda create -n brd|brain-tumor-detect python=3.10
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
conda activate brd
conda deactivate


# 启动 windows powershell debug
$env:FLASK_APP="app.py"
$env:FLASK_DEBUG=1
flask run
```
