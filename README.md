# CV-Chess - A computer vision-based chess robot
![alt text](https://github.com/jmarangola/cv-chess/blob/main/IMG_1830.jpg?raw=true)

# Runnable Scripts and Commands 
All .ipynb files should run when the proper path is added to the respective files. In the README.md for the chess_piece_classifier folder, the necessary datasets are linked.  

For the neural network code, go to "chess-piece-classifier folder" and the main neural network will be called "PieceClassifier.ipynb"

All robotics code can be found in the "robotics" folder in "core". 

All other python programs mainly pertain to image preprocessing and can be found in the "vision" folder under "core". However, these don't need to be ran to run the neural network as the data that is provided has already been through the necessary preprocessing. 


# Final Report Group Breakdown <br />
Section 1: Alex Benanti and Bryan Kim <br />
Section 2: Bryan Kim, John Marangola <br />
Section 3: Bryan Kim, John Marangola, Alex Benanti, and Fabio Costa  <br />
Section 4: Alex Benanti, Fabio Costa, and John Marangola <br />
Section 5: Alex Benanti <br />

# Project Contribution High level Overview
- Edge and corner detection experiments: Fabio Costa, John Marangola <br />
- Printing and designing chess pieces: John Marangola, Fabio Costa <br />
- Fixing camera pose: Alex R., John Marangola
- Imaging Jetson, building realsense dependencies from source: Bryan Kim, John Marangola
- Image preprocessing: Fabio Costa, John Marangola
- Warp transform (enbedded in preproccessing): Bryan Kim, Alex B.
- Robotics: John Marangola <br />
- Dataset Collection: All <br />
- Pipeline for Image Classifier: Fabio, Alex B., and Alex R. <br />
- Neural Network (Including Pandas Framework): Fabio, Alex B., and Alex R. <br />

# Non-trivial individual Program Contribution (by person)

Alex Benanti
  - ChessPiece_Color_Model.ipynb
  - PieceClassifier.ipynb
  - PipelineForData.ipynb
  - preprocessing.py

John Marangola 
  - preprocessing.py 
  - core/robotics/ folder
  - dataset_managment.ipynb
  - dataloader.py
  - collection.py
  - realsense_utils.py
  - uploader.py
  - corner_and_edge_experiments.ipynb

Fabio Costa 
  - ChessPiece_Color_Model.ipynb
  - PieceClassifier.ipynb
  - PipelineForData.ipynb
  - preprocessing.py
  - corner_and_edge_experiments.ipynb

Bryan Kim 
  - preprocessing.py

Alexandre Roth 
  - PipelineForData.ipynb
  - ChessPiece_Color_Model.ipynb
  - hardcode.py
