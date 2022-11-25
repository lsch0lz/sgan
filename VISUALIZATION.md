# Visualize the results of trained model

The visualization puts all the predictions and ground truth data together in a single plot. 
The Script iterates over all the trajectory's and stores them in seperate variables.
At the end the total of all trajectory's will be plotted/animated.

Execution:
```python visualize.py --model_path path\to\your\model.pth```

The script will produce a ````.mp4```` and a ```.png``` file which contain the Ground Truth 
(Dashed line) and the prediction (Dotted Line).

You can modify those visualizations by changing line ```line 128``` in ```visualize.py```.