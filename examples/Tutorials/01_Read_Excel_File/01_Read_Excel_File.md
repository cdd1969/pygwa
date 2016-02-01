# Tutorial 01: Read Excel File

One of the most convinient way so store timeseries data is to use tables or spreadsheets. This tutorial covers how to load information from the EXCEL spreadsheet into **PyGWA** for further processing.

##### Step 1
Open New Flowchart (Menu -> Flowchart -> New).
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705885/2849658c-c879-11e5-93f4-53c3d82c6aa0.png" width="50%"></img>

##### Step 2
Find Node ***readXLS*** in Node Library by typing in search field.
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705884/2848d324-c879-11e5-8f73-55081bd704f6.png" width="50%"></img>

##### Step 3
Now add the Node ***readXLS*** to the flowchart canvas by drag'n'dropping the node's name to the black area. A graphical representation of the Node should appear on canvas (you can adjust zoom level by scrolling the mouse wheel). New Node has name "readXLS.0". Note that the dock-widget *Node Controls* (bottom-left part of the window) now shows the name of the selected node (newly created nodes are automatically selected) and UI-controls of the "readXLS.0".
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705886/284bb698-c879-11e5-9294-cc2bea479ae0.png" width="50%"></img>

##### Step 4
Now select the file to load by pressing the button "Select File" in the *Node Controls* dock-widget. A pop-up selection window appears. Select the test data-file under *pygwa/examples/Tutorials/test_data.xlsx* and click "Open". The pop-up window closes.
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705887/284c78da-c879-11e5-8871-7f5aac4142e9.png" width="50%"></img>

##### Step 5
Now the file is selected by not yet loaded! You may adjust some parameters in UI-controls (see *readXLS Node Help*), that will affect the way the data will be loaded. Finally click "Load File" button in the Node UI-controls. This will run the script behind the scenes and inform user of the loading status. Select the node "readXLS.0" by clicking it on the canvas (the selected node is highlighted) and inspect the dock-widget *Selected Node* (bottom under the black canvas). An object of loaded data is placed in the output terminal "output" of the "readXLS.0" node. At this step the data is loaded. You may want to check what exactly has been loaded. To do so, proceed with steps 6-8.
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705888/28678e90-c879-11e5-9905-68a0e6272705.png" width="50%"></img>

##### Step 6
To visualize the loaded data add node ***QuickView*** the same way as described in steps 2,3. Node "QuickView.0" appears.
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705891/2868c99a-c879-11e5-8ef9-e87a677339a1.png" width="50%"></img>

##### Step 7
In order to pass the data from node "readXLS.0" to node "QuickView.0" connect output terminal "output" of "readXLS.0" with input terminal "in" of "QuickView.0" by dragging the line between them. Both terminals are colored with green indicating, that data flow occured without errors.
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705889/2867ebe2-c879-11e5-8fb2-8e02923715f2.png" width="50%"></img>

##### Step 8
Select the node "QuickView.0" and click two buttons "View Table", "View Plot" located in the UI-controls dock-widget. Two windows appear.
**NOTE:** you may select and copy data from the ***QuickView: Table View*** and then paste it into EXCEL or text-file! To do so, select cells and press Ctrl+C or open context menu by pressing right mouse button. Then you may paste your data by pressing Ctrl+V.
<img style="float: middle;" src="https://cloud.githubusercontent.com/assets/14345411/12705890/28682206-c879-11e5-9631-4d6f6db24495.png" width="50%"></img>