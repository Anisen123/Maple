# MAPLE
The MAPLE framework is an innovative system for AI applications to (1) recommend various model compositions (2) recommend appropriate system configuration based on the application’s non-functional requirements (3) estimate the performance and cost of deployment on cloud for the chosen design.
This repository contains the python code for the interface for creating and deploying an ML-pipeline.

## Instructions
1. Tested on Python 3.9
2. Additional packages required: PyQt5, numpy, selenium, re, sqlite3. 
3. Run MainWindow.py
4. Set required attributes for model, cost, latency on left. Press Enter to get list of 
   applicable models.
5. Click on model in list 'applicable models' to select, and double-click on canvas to drop at location. 
6. To insert additional components except connector: Click on component to select and 
   double-click on canvas to drop at location. 
7. To insert arrow between two components: Select two components(click + cntrl for 
   multiple selection) and click on connector to add arrow between them. 
8. Double-click on model to get corresponding information.
9. Components can be dragged and dropped within canvas.
10. Select components(also applicable for arrow) and press backspace to delete components.
11. Click on connector to reverse direction.
12. To add model to sql database: click on add model.
13. To edit/delete model in sql database: click on 'edit/delete model' first. This is model-edit mode 
    and does not allow models to be added to diagram. Now click on model name to be edited/deleted to do so.
14. Exit model-edit mode by once again clicking on 'edit/delete model' button.
15. For modifying transformers in sql database: do same as above three points with 'Transformer buttons'.
16. Get context menu for model or other objects by right clicking on it, then select option as required.
17. Add application in saved application list by clicking corresponding button and filling pop-up form as required. Application attributes will show up on double clicking in application list.
18. Add config in saved configs list by clicking corresponding button and filling pop-up form as required. Config attributes will show up on double clicking in config list.
19. ObjectData.db is an sqlite3 database which contains two tables - 'models' and 'Transformers'.
