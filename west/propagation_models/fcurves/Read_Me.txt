NOTES ON CURVES:

Some brief notes on the CURVES program are contained at the beginning of the text file CURVES.F.  
This page contains some supplementary notes that may be of interest to users, in no particular order.  
Please read it in its entirety.

WE DO NOT RECOMMEND THAT YOU USE THESE FILES UNLESS YOU DOWNLOAD THEM
DIRECTLY FROM http://www.fcc.gov/mb/audio/bickel/archives/fmtvcurves.zip YOURSELF!!!
NEVER run a .exe file from an unknown source.  If you do, run a virus scan on all files immediately 
afterwards using up-to-date virus software, to insure that no infection has taken place.  .   

The files and source code contained herein are NOT SUPPORTED.  Use them at your own risk.  We
do not guarantee the code to be free of errors, nor will any results obtained through use or 
misuse of this code invalidate any official source or finding.  Any liability is assumed by the user,
not the FCC or its employees.    But, hey, it's free!

The file FMTVCURVES.EXE is a command-line "console" program that may be run on Windows 
machines (Windows 95 or later).  Click on it to start it, or call it by entering "fmtvcurves.exe" in 
dos.exe (Windows 95, 98) or cmd.exe (Windows 2000, XP)  (after changing to the directory you
saved this program in).

FMTVCURVES.BAT is a small batch file that changes the background and text colors from 
black and white on Windows 2000 or XP to other colors.  Click on it, or enter "fmtvcurves.bat"  
on the command line to start it.  This will have no adverse effect in Windows 95 or 98, but it
won't do anything helpful either.  Users on other platforms will not need the batch file.  

As implemented here, the CURVES.F file sets up the parameters by a short question-and-answer
approach.  Output is displayed on screen, and there is an option to save the results to a text file
(c:\temp\FMTVcurves.txt -- NOTE:  you may need to create the c:\temp directory).  The
working routines are contained in CURVES-SUBROUTINES.F.  

If this code is to be translated to another programming language, an automated translator is
suggested.  ITPLBV.F in particular is a very compressed subroutine and will be very difficult 
to translate manually.  The F2C compiler that can be downloaded with lcc-win32
(search for "lcc-win32" and "fortran.exe" on the Internet ) is capable of such translation, 
but be aware that the translated Fortran-to-C code is not readily readable. 

Fortran source code is included.  In general, the code has not been optimized.  This program 
has been independently compiled with Compaq Visual Fortran 6.6 and lcc-win32 
(including the fortran.exe F2C compiler).  

There is no equation to generate the propagation curves represented in this program.  The
various nonlinear curves are determined from a table of points, contained in the subroutine
tvfmfs_metric.f  The points were developed on the basis of measured field strengths under 
various conditions,  primarily in the 1930s and 1940s.  (See the documents at
http://www.fcc.gov/mb/audio/engrser.html#CURVES1 for more information. )  These curves 
represent an average expected field strength at a given distance: this signal strength may be 
higher or lower at a given time or location based on many conditions, such as atmospheric 
conditions (including ducting effects) and intervening terrain.  This method does NOT
 incorporate Longley-Rice or Technical Note 101 calculations.   

You may compare the results to the FCC's on-line program at
http://www.fcc.gov/mb/audio/bickel/curves.html .

Dale Bickel  dale.bickel@fcc.gov  
Senior Electronics Engineer
Audio Division, Media Bureau
Federal Communications Commission

August 2003 

 
                                                                       --- *** ---

      