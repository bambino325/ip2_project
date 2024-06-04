import subprocess
import sys
import os

def install_virtualenv():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'virtualenv'])
    except subprocess.CalledProcessError:
        print("Error installing virtualenv.")
        sys.exit(1)

def create_virtualenv(venv_dir):
    try:
        subprocess.check_call([sys.executable, '-m', 'virtualenv', venv_dir])
    except subprocess.CalledProcessError:
        print("Error creating virtual environment.")
        sys.exit(1)

def install_requirements(venv_dir):
    try:
        if sys.platform.startswith('win'):  
            subprocess.check_call([os.path.join(venv_dir, "Scripts", "pip"), "install", "-r", "requirements.txt"])
        else:
            subprocess.check_call([os.path.join(venv_dir, "bin", "pip"), "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Error installing requirements.")
        sys.exit(1)

def main():
    install_virtualenv()

    venv_dir = "myenv"
    create_virtualenv(venv_dir)
    install_requirements(venv_dir)
    print("Requirements installed successfully.")

if __name__ == "__main__":
    main()
