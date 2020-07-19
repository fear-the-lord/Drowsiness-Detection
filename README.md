# Drowsiness Detection System 

## Motivation: 
According to the National Highway Traffic Safety Administration, every year about 100,000 police-reported crashes involve drowsy driving. These crashes result in more than 1,550 fatalities and 71,000 injuries. The real number may be much higher, however, as it is difficult to determine whether a driver was drowsy at the time of a crash. So, we tried to build a system, that detects whether a person is drowsy and alert him. 
## Running the system: 

### Step 1: 
Clone the repository into your system by: 
```bash 
git clone https://github.com/fear-the-lord/Drowsiness-Detection.git
```
Or directly download the zip.

### Step 2: 
Download the file <b>shape_predictor_68_face_landmarks.dat</b><a href = "https://drive.google.com/file/d/14weZIclFncz8BMOmrkLp9PadLIccbSBa/view?usp=sharing">here.</a>. Make sure you download it in the same folder. 

### Step 3: 
Install all the system requirments by:
```bash 
pip install -r requirements.txt
```

### Step 4: 
After the system has been setup. Run the command: 
```bash 
python app1.py
```

### Step 5: 
Open your browser and in the search bar type: 
<b>localhost:8000</b> as this port is mostly used by flask. 
In case, this port is not available in your system, flask will try to use another port. The port number will be displayed in the command prompt.
So, type in the same port number in that case as: 
<b>localhost:<port_number></b>.
  
After all these steps have been completed successfully, you will see a web page opening up in the browser. Now you are free to explore the system.


