import subprocess
import os

def get_git_status():
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    with open('git_files.txt', 'w') as f:
        f.write(result.stdout)

if __name__ == '__main__':
    get_git_status()
