# Lerobot Software  

### Initial Setup
The first step for the software of the arms is to install the repository. I have been following the video tutorials from hugging face. Thus I needed to search for the repository which corresponds to the video tutorials. You can clone the repository using:
```
git clone https://github.com/huggingface/lerobot.git
```
once you are in the lerobot folder with `cd lerobot` you can go to the commit which follows the youtibe tutorials using:
```
git checkout c0da806
```
Now you should be in the same commit as the one which the youtibe titorials follow.

you should set up a conda environment as the intallation requires python 3.10. You can make a conda environment whith:
```
conda create -n robotenv python=3.10

```
I named my environment "robotenv" but you can name it whatever you want. Once the environment has been created you can activate it using 
```
conda activate robotenv

```
To summerize up until this point, you have cloned the necessary repository, went into the lerobot folder, made a conda environment with python 3.10, and activated the environment. Now you must actually install the code so you can use it. You can do this by running:
```
pip install -e ".[koch]"

```

### Start Up
Once you have everything isnatlled, you can begin the startup process. You can start by clamping down the arms and plugging in the power supplies. The follower arm should use the 12v power supply and the leader arm should use the 5v power supply.

You should already be in the lerobot folder and have the conda environment activated. You will need to bind the usb ports to WSL, I run powershell as an admin to do this. Without anything plugged in use:

```
usbipd list

```
This will show you all the usb devices currently connected and their busid
### Calibration

### Teleoperation

### Data Collection