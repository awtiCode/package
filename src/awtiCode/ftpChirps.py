# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 08:21:44 2022

@author: Demiso
"""
#use this to download data from ftp

from ftplib import FTP
import os, sys, os.path

def ftpChirpsExplore(directory = '/pub/org/chg/products/'):
    ftp = FTP("ftp.chc.ucsb.edu")
    ftp.login()
    ftp.cwd(directory)
    answer = 'start'
    chosen_directory = directory
    while True:
        file_list = ftp.nlst()
        print('Under directory '+chosen_directory+', there are the following directories and/or files: ')
        print(file_list)
        answer = input('Type any directory you want to go into. To go back to the original directory, type \'back\'. To stop exploring, type \'quit\'. To go one directory up, type \'up\'.\n>>>')
        if answer.lower().startswith('q'):
            print('You are leaving the ftp server.')
            break
        elif answer == 'back':
            print('Going back to directory '+directory)
            chosen_directory = directory
            ftp.cwd(directory)
        elif answer == 'up':
            bindex = chosen_directory[-2::-1].find('/')
            chosen_directory = chosen_directory[:-1-bindex]
            print('Going up to directory '+chosen_directory)
            ftp.cwd(chosen_directory)
        elif answer in file_list:
            try:
                ftp.cwd(chosen_directory+answer+'/')
                chosen_directory += answer+'/'               
            except:
                print('It was not possible to go into '+chosen_directory+answer+'/. Please select another.')
        else:
            print('Input was not clear.')
    ftp.quit()

def getFileList(directory):
    #Connecting to the ftp server
    ftp = FTP('ftp.chc.ucsb.edu')
    ftp.login()
    #Changing to the given directory
    print ('Changing to ' + directory)
    try:
        ftp.cwd(directory)
    except:
        print('The given directory does not exist. Please provide a valid Chirps ftp directory, under which there is the file with the given filename.')
        ftp.close()
        return
    filelist = ftp.nlst()
    ftp.close()
    print('List of '+str(len(filelist))+' files found under directory '+directory+'.')
    print('You can use the directory in combination with any of the filenames in the function downloadChirps, to download that specific file.')
    return filelist

def downloadChirps(directory,filename,local_folder=None):
    
    #Connecting to the ftp server
    ftp = FTP('ftp.chc.ucsb.edu')
    ftp.login()
    #Changing to the given directory
    print ('Changing to ' + directory)
    try:
        ftp.cwd(directory)
    except:
        print('The given directory does not exist. Please provide a valid Chirps ftp directory, under which there is the file with the given filename.')
        ftp.close()
        return

    #Setting up local file, requesting (and downloading) file from server, and writing it to local file.
    if local_folder == None:
        print('No local folder given. The file will be saved in your current working drectory.')
        local_filename = filename
    else:
        local_filename = os.path.join(local_folder, filename)
    
    file = open(local_filename, 'wb')
    
    try:
        print('Starting to download file. This might take a while...')
        
        ftp.retrbinary("RETR " + filename, file.write)    
        file.close()
    except:
        print('Something went wrong. Download is not succeeded.')
        file.close()
        ftp.quit()
        return
    print('Download finished. File saved as '+local_filename+'.')
    ftp.quit()