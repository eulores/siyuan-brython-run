from browser import document, window, ajax, run_script
from browser.html import BUTTON
import json


widgetID = window.frameElement.parentElement.parentElement.dataset.nodeId
codeID = None
widgetLabel = 'Run Python code'


def fetch(url, method="POST", **kwds):
    if 'ID' in kwds:
        kwds['id'] = kwds['ID']
    req = []
    def feedback(rs):
        nonlocal req
        req = rs
    getattr(ajax, method.lower())(url, blocking=True, headers={'Content-Type':'application/json'}, mode="json", timeout=1, data=json.dumps(kwds), oncomplete=feedback)
    return req.json


def loadCode():
    global widgetLabel
    global codeID
    r = fetch('/api/attr/getBlockAttrs', ID=widgetID)
    if 'custom-label' in r['data']:
        widgetLabel = r['data']['custom-label']
    if 'custom-python' in r['data']:
        codeID = r['data']['custom-python']
        r = fetch("/api/query/sql", stmt=f"select * from blocks where id='{codeID}'") # security fail: sql code injection!
        if len(r['data'])==1:
            return r['data'][0]['content']
    return False


def clickme(ev):
    global widgetID, codeID
    code = loadCode()
    if code:
        # exec(code)
        run_script(f'widgetID="{widgetID}"\ncodeID="{codeID}"\n'+code)
    else:
        r = fetch('/api/block/insertBlock', dataType="markdown", nextID=widgetID, data="""\
```python
# Write your Python code here!
# More details at https://brython.info/

from browser import alert

# This gets printed to the console (open Developer's tools).
# The output can be reset by setting sys.stdout to an object with a method write().
print('Hello World!')

# This should pop up on the browser
alert("Hello World!")
```""")
        codeID = r['data'][0]['doOperations'][0]['id']
        r = fetch('/api/attr/setBlockAttrs', ID=widgetID, attrs={"custom-python":codeID, "custom-label":widgetLabel})
        document["clickme"].text = widgetLabel


if loadCode():
    document <= BUTTON(widgetLabel, Id='clickme')
else:
    document <= BUTTON("Initialize", Id='clickme')
document["clickme"].bind("click", clickme)
