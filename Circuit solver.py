import sys          #importing necessary libraries
from numpy import*

class abc:        #defining class for elements                   
  
  def __init__(self,token):      #constructor 
    self.token=token
    self.node1=self.token[1]
    self.node2=self.token[2]
    
    if(len(self.token)==5):     #DC voltage and current source 
      self.value = float(self.token[4])
    
    if(len(self.token)==6):     #AC voltage and current source
      V=float(self.token[4])/2
      phase=float(self.token[5])
      self.value=V*complex(cos(phase),sin(phase))
    
    if(len(self.token)==4):    #R, L, C 
        self.value = float(self.token[3])
    

CIRCUIT = '.circuit'
END = '.end'

#count stores the line no. at which .circuit and .end occurs
circuit_count=0
end_count=0

#flag raises if .circuit and .end is found in the netlist file
circuit_flag=0
end_flag=0

element=[]     #list for storing objects of class abc
ac_flag=0      #Flag raises if the circuit has AC source

cktfile=sys.argv[1]
  
  #checking if given netlist file is of correct type 
if not cktfile.endswith(".netlist"):      
      print("Invalid File type")
else:
    with open(sys.argv[1]) as f:
     lines = f.readlines()
     for x in lines:
        circuit_count+=1
        if CIRCUIT == x[:len(CIRCUIT)]:
          a = lines.index(x)
          a+=1                 #To start with the index of the next line
          circuit_flag+=1
          break     
     for x in lines:
        end_count+=1
        if END == x[:len(END)]:
            end_flag+=1
            break
     if end_flag==0:    #If .end is not found then end_count is set to 0
          end_count=0
     if circuit_flag==0: #If .circuit is not found then circuit_count is set to 0
          circuit_count=0
      
      #checking if .circuit and .end are present as per the circuit definition
     if circuit_count>=end_count:
         print("invalid circuit definition")
         exit()
      
     else:
          for y in lines[a:]:   # a is the index of the line just after .circuit
          
        #To stop reversing the lines once .end is identified
             if END == y[:len(END)]:
                break
             else:
               element.append(abc(y.split()))
               if (y[0]=='V' and y.split()[3]=='ac'):
                ac_flag+=1
    
          row_max=0   #This variable stores the number of rows and columns of M matrix
          
          for t in element:
            if (t.node1!='GND'):   
                 n1=int(t.node1)   #converting string to integer
                 if(n1>row_max):
                   row_max=n1
            if (t.node2!='GND'):
                 n2=int(t.node2)
                 if(n2>row_max):
                   row_max=n2
          last=row_max
          node_max=row_max         #node_max stores the number of nodes in the ckt
           
          for t in element:
                 if(t.token[0][0]=='V'):    #To add rows for currents passing through voltage sources 
                   row_max+=1
                 
     if(ac_flag>0):        #AC Analysis
      
      if (lines[end_count].split()[0]=='.ac'):
        w=float(lines[end_count].split()[2])       #frequency of the source
      
      M=zeros((row_max,row_max),dtype=complex)  #initializing zero M matrix
      I=zeros((row_max,1),dtype=complex)        #initializing zero I matrix
      
      for t in element:
          if (t.node1!='GND'):
              n1=int(t.node1)       #converting string to integer 
          if (t.node2!='GND'):     
              n2=int(t.node2)         
          
          
          if (t.token[0][0]=='R'):           #Matrix modification for Resistor 
            if (t.node2=='GND'):
                M[n1-1][n1-1]+=reciprocal(t.value)     #Add reciprocal of Resistance
            elif (t.node1=='GND'):
                M[n2-1][n2-1]+=reciprocal(t.value)
          
            else:
              M[n1-1][n1-1]+=reciprocal(t.value)    #Add reciprocal of Resistance
              M[n2-1][n2-1]+=reciprocal(t.value)
              M[n2-1][n1-1]+=-reciprocal(t.value)
              M[n1-1][n2-1]+=-reciprocal(t.value)
          if (t.token[0][0]=='I'):          #Matrix modification for current source
              if (t.node2=='GND'):
                I[n1-1][0]+=-t.value
              elif (t.node1=='GND'):
                I[n2-1][0]+=t.value
              else:
                I[n1-1][0]+=-t.value
                I[n2-1][0]+=t.value

          if (t.token[0][0]=='V'):         #Matrix modification for voltage source
              if (t.node2=='GND'):
                M[n1-1][last]+=-1
                M[last][n1-1]+=-1
                I[last][0]+=t.value
              elif (t.node1=='GND'):
                M[n2-1][last]+=1
                M[last][n2-1]+=1
                I[last][0]+=t.value
              else:
                M[n1-1][last]+=-1 
                M[n2-1][last]+=1
                M[last][n1-1]+=-1 
                M[last][n2-1]+=1
                I[last][0]+=t.value
          last+=1
          if (t.token[0][0]=='C'):        #Matrix modification for Capacitor
            if (t.node2=='GND'):
                M[n1-1][n1-1]+=complex(0,2*pi*w*t.value)      #reciprocal of impedance
            elif (t.node1=='GND'):
                M[n2-1][n2-1]+=complex(0,2*pi*w*t.value)
            else:
              
              M[n1-1][n1-1]+=complex(0,2*pi*w*t.value)      #reciprocal of impedance
              M[n2-1][n2-1]+=complex(0,2*pi*w*t.value)
              M[n1-1][n2-1]+=-complex(0,2*pi*w*t.value)
              M[n2-1][n1-1]+=-complex(0,2*pi*w*t.value)
              
          if (t.token[0][0]=='L'):      #Matrix modification for Inductor
            if (t.node2=='GND'):
                M[n1-1][n1-1]+=reciprocal(complex(0,2*pi*w*t.value))        #reciprocal of impedance
            elif (t.node1=='GND'):
                M[n2-1][n2-1]+=reciprocal(complex(0,2*pi*w*t.value))
            else:
              
              M[n1-1][n1-1]+=reciprocal(complex(0,2*pi*w * t.value))       #reciprocal of impedance
              M[n2-1][n2-1]+=reciprocal(complex(0,2*pi*w * t.value))
              M[n1-1][n2-1]+=-reciprocal(complex(0,2*pi*w * t.value))
              M[n2-1][n1-1]+=-reciprocal(complex(0,2*pi*w * t.value))
      
      print("M matrix: ")         #Printing final outputs
      print(M)
      print('\n')
      print("I matrix:")
      print(I)
      print('\n')
      x=linalg.solve(M,I)
      for w in range(node_max):
          print("Voltage at node %d: " %(w+1), end=' ')
          print(x[w])
          
      for w in range(row_max-node_max):
          print("Current through voltage source %d: " %(w+1), end=' ')
          print(x[w+node_max])
          
      
     else:          #DC Analysis
      
       M=zeros((row_max,row_max),dtype=float)
       I=zeros((row_max,1),dtype=float)
      
       for t in element:
          if (t.node1!='GND'):
              n1=int(t.node1)        #converting string to integer
          if (t.node2!='GND'):
              n2=int(t.node2)
          
          
          if (t.token[0][0]=='R'):    #Matrix modification for Resistor
            if (t.node2=='GND'):
                M[n1-1][n1-1]+=1/(t.value)
            elif (t.node1=='GND'):
                M[n2-1][n2-1]+=1/(t.value)
          
            else:
              M[n1-1][n1-1]+=1/(t.value)
              M[n2-1][n2-1]+=1/(t.value)
              M[n2-1][n1-1]+=-1/(t.value)
              M[n1-1][n2-1]+=-1/(t.value)
        
          if (t.token[0][0]=='I'):       #Matrix modification for Current source
              if (t.node2=='GND'):
                I[n1-1][0]+=-t.value
              elif (t.node1=='GND'):
                I[n2-1][0]+=t.value
              else:
                I[n1-1][0]+=-t.value
                I[n2-1][0]+=t.value

          if (t.token[0][0]=='V'):        #Matrix modification for voltage source
              if (t.node2=='GND'):
                M[n1-1][last]+=-1
                M[last][n1-1]+=-1
                I[last][0]+=t.value
              elif (t.node1=='GND'):
                M[n2-1][last]+=1
                M[last][n2-1]+=1
                I[last][0]+=t.value
              else:
                M[n1-1][last]+=-1 
                M[n2-1][last]+=1
                M[last][n1-1]+=-1 
                M[last][n2-1]+=1
                I[last][0]+=t.value
              last+=1

       print("M matrix: ")       #Printing final outputs
       print(M)
       print('\n')
       print("I matrix:")
       print(I)
       print('\n')
       x=linalg.solve(M, I)          
       
       print("Voltage at GND: 0")
       for w in range(node_max):                           
           print("Voltage at node %d: %f" %(w+1, x[w]))
           
       for w in range(row_max-node_max):
           print("Current through voltage source %d: %f" %(w+1, x[w+node_max]))   
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
      
      
      