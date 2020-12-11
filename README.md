## notebook
This repo is for any notes in tech study.

#### PBI free account application
[PBI Hub](https://pbihub.cn/blog/190)

#### Free course website
[Free course](https://courses.analyticsvidhya.com/)
[Free ML course I enrolled](https://courses.analyticsvidhya.com/courses/take/get-started-with-scikit-learn-sklearn/texts/10754763-welcome-to-this-course)

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
