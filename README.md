# Environment

- Python 3.10
- Windows 10

# Setup

```bash
pip install -r requirements.txt
```

# Run

```bash
python main.py
```

# Build portable executable

Portable does not require Python to be installed on the machine.

```powershell
Expand-Archive -Path .\Tesseract-OCR.zip -DestinationPath .\
Expand-Archive -Path .\poppler.zip -DestinationPath .\
pip install -r requirements.txt
pyinstaller main.spec
cp config.conf ./dist/main/
```

`./dist/main/` is the portable executable directory.

# Documentation

Once the server is running, you can access the documentation at:

http://127.0.0.1:8000/api/v1/docs

# Test files

You can use the `test_document.pdf` file to test the API.