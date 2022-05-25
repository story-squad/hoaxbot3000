#Research question: 
Will using a list of word embeddings from words with opposite meanings and measuring the vector distance between them give us a usable baseline
##Assumptions:
1) some baseline is needed to normalize results of finding the embedding difference when evaluating ai personality
##Definitions
- model_set1 = {["yes","no"]}
- model_set2 = {[]}
- test_set = [("yes","no"),("good","bad"),("up","down"),("north","south"),("hard","soft"),("liquid","solid"),("summer","winter")]
##Hyptheses:
1) finding the total difference between two opposite word vectors will give a difference that is within 25% of the test set
2) finding the maximum differnce between any combination of two words in a sample list will provide a difference that is within 25% of the test set
##Testing environment
The notebooks for these hypotheses will be in the same root folder as this document, and will
possess the following basic structure.
- Results of !pip list
- System information, OS, CPU, GPU
- Statement of Hypothesis to be tested
  - explanation of how it relates to research question
- cells to load data sets
  - each cell will have an explanation of data that is loaded
- Summery of experiments to be performed
- Experimental sections contain
  - statement of experiment
    - how it relates to hypothesis 
  - Explanation of methodology
  - code cells to execute experiment
  - analysis of experimental results
- Analysis section explaining results and proving/disproving the hypothesis

## Hypotheses notebooks
1) does_synthetic_data_improve_mae.ipynb will test, "Training a 3 layer fully connected network on synthetic data first will improve MAE on user generated data."
   1) This notebook will establish the baseline model which will include
      1) training over 1000 epochs
      2) training completed with random initialization as well as constant intialization
      3) will provide a range of expected scores
      4) will use model performance on the user generated dataset as the validation score.
      
2) conv_layers_improve_mae.ipynb will test, "Adding convolution layers to the beginning of the model will improve MAE to below baseline levels."
   1) This notebook will compare the results of 3 different convolutional models to the baseline model
3) grayscale_will_improve_mae.ipynb will test, "converting the input to grayscale and providing x and y axis value distribution information will lower MAE compared to the baseline model."
   1) this notebook will convert the dataset to black and white first and then test vrs the baseline model
4) sliceing_will_improve_mae.ipynb will test, "Slicing the image into slices of 1/3 and only giving the model the corners will lower MAE of the baseline."
   1) this notebook will provide a model that slices the input up and and test it against the baseline model


---=== link to results