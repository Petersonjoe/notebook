## NoteBook
This repo is for any notes in tech study.

#### Visualization materials
 - [China map shape file](http://bbs.3s001.com/thread-133690-1-1.html)

#### PBI free account application
 - [PBI Hub](https://pbihub.cn/blog/190)

#### Free course website
 - [Free course](https://courses.analyticsvidhya.com/)
 - [Free ML course I enrolled](https://courses.analyticsvidhya.com/courses/take/get-started-with-scikit-learn-sklearn/texts/10754763-welcome-to-this-course)
 - [Scikit-learn tutorial with real data set](https://scikit-learn.org/stable/auto_examples/applications/plot_outlier_detection_wine.html#sphx-glr-auto-examples-applications-plot-outlier-detection-wine-py)

#### Sublime text 3 setting for unicode chars

Create mypython.sublime-build file under sublime text user folder, and select this build file as the build system.

In the build file, below content is the simplest one for settings:
```json
{
    "cmd": ["\\path\\to\\your\\env\\folder\\Scripts\\python.exe", "$file"],
    "selector": "source.python",
    "file_regex": "^\\s*File \"(...*?)\", line ([0-9]*)",
    "env": {"PYTHONIOENCODING": "utf8"}
}
```

#### Windows Batch Schedule Tasks

 - [Batch Schedule Tasks](https://blog.csdn.net/qq_31176861/article/details/90901336)
