Date: May 1st, 2026 

This is a readme for the script to make a xyz file from a folder of DFT calculations using Gaussian, where each calculation has a folder with a .log file and other files in it (the input .com/.gjf, the .chk, the .log, and maybe others).

KAG created this script with the help of AI (ChatGPT IIRC) and implemented it using Python 3.9 via IDLE.

The script helps speed up data processing for DFT calculations where you need to make a .xyz file of all your optimized geometries for publication. Prior to this, I would open each .log file from Guassian in GaussView, then save as .mol2, then use another softeware, Mercury from CCDC, to save as .xyz, then use notepad++ to copy and past the xyz coords into a single .xyz file. It was annoying and time-consuming, so why not automate it? 

I used Chatgpt to make the script.

I am sure it could be done better (I don't know how to code), but it's worked for me! 
