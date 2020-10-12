# Project Name: CIS 41B - Lab 3:  web scraping and data storage with requests, beautifulsoup, sqlite3
# Name :        Yin Chang
# Discription:  Write an application that lets the user search for Covid-19 data of countries of the world
# Module:       lab3front.py
# Discription:  will read from the SQL database to display data to the user

import matplotlib
matplotlib.use('TkAgg')               	                         # tell matplotlib to work with Tkinter
import tkinter as tk                      	                 # normal import of tkinter for GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Canvas widget
import matplotlib.pyplot as plt	                                 # normal import of pyplot to plot
import  tkinter.messagebox  as  tkmb
import sqlite3

'''-------------------Defining dialogWin class--------------------'''
class dialogWin(tk.Toplevel) : # inherit from tkinter Tk class	
    """ A dialog window shows up to let the user chooses countries."""
    def __init__(self, master,countries) :
        """ A  listbox that can show 10 lines of text. Each line of text is a country name from the database, the list of names are sorted in alphabetical order."""
        super().__init__(master)
        self.title("Choose Country")
        self.geometry("+100+100")
        self._F = tk.Frame(self)
        self._F.grid()
        self._S = tk.Scrollbar(self._F)
        self._LB = tk.Listbox(self._F, height=10, width=20, selectmode="multiple",yscrollcommand=self._S.set)
        self._S.config(command=self._LB.yview)
        self._LB.grid()
        self._S.grid(row=0,column=1,sticky='ns')
        self._LB.insert(tk.END,*countries)  
        tk.Button(self, text="OK", command=self._setChoice).grid(row=2,pady=2)  # click OK to commit the choice and close the window
        
        self.transient(master) # or on the main window to start another event until the dialog window closes. 
        self.focus_set()       # It should have the focus. 
        self.grab_set()        # The user should not be able to click on any plot window 
        self.protocol("WM_DELETE_WINDOW",self._close)
    
    def _setChoice(self):
        """ Once the user click OK, commit the choice and close the window """
        if self._LB.curselection():
            self._choice = self._LB.curselection()
            self.destroy()
        else:
            self._close()
                
    def getChoice(self):
        """ A Getter for User's choice """
        return self._choice
    
    def _close(self):
        """ If User click X, clear choice """
        self._choice=()
        self.destroy()
        
'''-------------------Defining plotWin class--------------------'''
class plotWin(tk.Toplevel) :	         # inherit from tkinter Tk class	
    """ Plot the number of cases for each country."""
    def __init__(self, master,selectedData) :
        """ There should be a title, y-axis label, and the xticks should be the country names."""
        super().__init__(master)
        self.transient(master)
        self.title("Covid-19 Cases")
        fig = plt.figure(figsize=(8, 5)) 
        countryName = [line[0] for line in selectedData] 
        number = [line[1] for line in selectedData]
        plt.bar(countryName,number,align="center")
        plt.title("Number of Cases for Chosen Countries")          # Add a title
        plt.ylabel("Number of Cases per 1M people")                # Add y-axis label
        plt.xticks(rotation=75)                                    # Add x-ticks as country name
        plt.tight_layout()         
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid()
        canvas.draw()        
               
'''-------------------Defining displayWin class--------------------'''
class displayWin(tk.Toplevel) : # inherit from tkinter Tk class	
    """ A dialog window shows up to let the user chooses countries."""
    def __init__(self, master,title,fileldName,data,*args) :
        """ A  listbox that can show 10 lines of text. Each line of text is a country name from the database, the list of names are sorted in alphabetical order."""
        super().__init__(master)
        self.title(title) 
        self._listboxName=[item for item in range(1,len(fileldName)+1)] # Create a variable list for each field 
        needSB = False                                                  # Create a boolean variable to check if the window needs a scrollbar (default to false)
        index = 0                                                       # Create an index variable to go over each field and column position
        boxHeight = 20                                                  # set the default listbox height to 20
        self._F = tk.Frame(self)
        self._F.grid()
        
        if len(data)>20: # Check if the window needs a scrollbar
            needSB = True
            self._S = tk.Scrollbar(self._F,command=self._yview)  
            boxHeight = 10
                   
        for item in self._listboxName: 
            tk.Label(self._F, text=fileldName[index]).grid(row=0,column=index)             # Create a label for each field
            item = tk.Listbox(self._F, height=boxHeight, width=17, selectmode="multiple")  # Create a listbox for each field
            if needSB:
                item.config(yscrollcommand=self._S.set) 
                item.bind("<MouseWheel>", self._OnMouseWheel)
            item.grid(row=1,column=index)
            columnData = [elem[index] for elem in data] # Fetch the data of the field
            item.insert(tk.END,*columnData)             
            self._listboxName[index]=item               # Save the variable name into list
            index +=1                                   # Move to next Field/column
        if needSB:
            self._S.grid(row=1, column=index, sticky="ns")
            
        if args: # If the window got a message argument, create a lebel for it.
            tk.Label(self, text=args[0]).grid(row=2)  
            
    def _yview(self,*args):
        """ Set the callback for all listboxes view function to change when the scrollbar is moved """
        for item in self._listboxName:
            item.yview(*args)
    def _OnMouseWheel(self, event):
        """ scroll listboxes together with the mousewheel """
        for item in self._listboxName:
            item.yview("scroll", event.delta,"units")    
        return "break"   # this prevents default bindings from firing, which would end up scrolling the widget twice
      
'''-------------------Defining mainWin class--------------------'''
class mainWin(tk.Tk) :
    """ The main window shows some statistics and 3 buttons for the user to view detailed data """
    def __init__(self) :
        """ Show 3 lines of statistics and 3 buttons"""
        super().__init__()
        try: 
            self._conn = sqlite3.connect('lab3.db')
            self._cur = self._conn.cursor()
            self._cur.execute("SELECT COUNT(*) FROM covid19Update WHERE Population > 0")
            numOfCountry = self._cur.fetchone()   # the total number of countries in the database
            self._cur.execute("SELECT TotalCases1Mpop,Deaths1Mpop FROM covid19Update WHERE Country='World'")
            num1Mpop = self._cur.fetchone()       # the number of Covid-19 cases/deaths per million people worldwide            
        except Exception as exceptObj: # If any of the file open is not successful, a messagebox window will show up
            tkmb.showerror("Error", str(exceptObj), parent=self)   
            exit()  # Terminate the program
                 
        self.title("Covid-19 Cases") 
        tk.Label(self, text= ("Worldwide: {} countries").format(numOfCountry[0])).grid(sticky='w',columnspan = 6)
        tk.Label(self, text= ("Worldwide: {} cases per 1M people").format(num1Mpop[0])).grid(row=1,sticky='w',columnspan = 6)
        tk.Label(self, text= ("Worldwide: {} deaths per 1M people").format(num1Mpop[1])).grid(row=2,columnspan = 6,sticky='w')
        tk.Button(self, text="New Cases", command=self._newCases).grid(row=3,column=0,columnspan = 1)
        tk.Button(self, text="Top 20 Cases", command=self._top20Case).grid(row=3,column=1,columnspan = 1)
        tk.Button(self, text="Compare Countries", command=self._processCountries).grid(row=3,column=2,columnspan = 1)
        self.protocol("WM_DELETE_WINDOW", self._endfct)

    def _newCases(self):
        """The callback function retrieves all countries with new cases from the database and sends it to the display window."""
        self._cur.execute('''SELECT Country,NewCases,NewDeaths
                             FROM covid19Update
                             WHERE Population > 0
                             ORDER BY NewCases DESC 
                             ''') # The countries are sorted in descending order by number of new cases.
        newCaseData = self._cur.fetchall()
        self._cur.execute('''SELECT NewCases,Continent 
                             FROM covid19Update 
                             WHERE Population = 0 and Country != 'World'
                             ORDER BY NewCases DESC''')
        topContinent=self._cur.fetchone() # highest number of new cases in a continent and the corresponding continent name    
        message = "Highest: {} new cases in {}".format(topContinent[0],topContinent[1])
        topWinTitle = "New Cases"
        fieldNames = ['Country','New Cases','New Deaths']
        displayWin(self,topWinTitle,fieldNames,newCaseData,message)
        
    def _top20Case(self):
        """ The callback function retrieves from the database the 20 countries with the highest number of cases per 1 million people, and sends it to the display window."""
        self._cur.execute('''SELECT Country,TotalCases1Mpop,Deaths1Mpop,Tests1Mpop
                             FROM covid19Update
                             WHERE Population > 0
                             ORDER BY TotalCases1Mpop DESC    
                             LIMIT 20
                             ''') # The countries are sorted in descending order by number of cases.
        top20Data = self._cur.fetchall()
        topWinTitle = "Top 20 Countries- Cases/1M"
        fieldNames = ['Country','Case/1M','Deaths/1M','Tests/1M']
        displayWin(self,topWinTitle,fieldNames,top20Data)
        
    def _processCountries(self):
        """ Call A dialog window shows up to let the user chooses countries then plot the chosen countries """
        self._cur.execute('''SELECT Country,TotalCases1Mpop
                             FROM covid19Update
                             WHERE Population > 0
                             ORDER BY Country ASC 
                             ''') # the list of country names are sorted in alphabetical order      
        dialogData = self._cur.fetchall()
        countries = [line[0] for line in dialogData]
        dialog = dialogWin(self,countries)
        self.wait_window(dialog)
        choices = dialog.getChoice()
        if choices: # If the user made 1 or more choices, fetch from the database the data for each choice, then send the data to the plot window.
            selectedData = [dialogData[index] for index in choices]
            plotWin(self,selectedData)
    def _endfct(self) :   
        """ A function to confirm if user really want to quit""" 
        askUser = tkmb.askokcancel("Confirm", "Are you sure you want to quit?", parent=self)    
        if askUser == True :        
            self.destroy()      # Close the window
            self._conn.close()  # Close the database when the GUI is closed.          
            print("Window Closed")        
            self.quit()        
            
def main():
    """ A main function to create a main wondow object and run it"""
    a = mainWin()
    a.mainloop()
    
main()
            
