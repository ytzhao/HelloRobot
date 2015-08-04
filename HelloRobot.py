import os
import unittest
import csv
import numpy
from __main__ import vtk, qt, ctk, slicer

#
# HelloRobot
#

class HelloRobot:
  def __init__(self, parent):
    parent.title = "Hello Robot"
    parent.categories = ["IGT"]
    parent.dependencies = []
    parent.contributors = [""] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Example
    """
    parent.acknowledgementText = """
    File""" # replace with organization, grant and thanks.
    self.parent = parent


#
# qHelloRobotWidget
#
class HelloRobotWidget:
  def __init__(self, parent = None):
    self.tnode = None
    self.strHostname = None
    self.times0 = 0

    self.chooseCell = False    
    self.connectTag = False
    self.registTag = False

    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    
    self.logic = HelloRobotLogic()

  def setup(self):
    # Collapsible button - Settings
    setCollapsibleButton = ctk.ctkCollapsibleButton()
    setCollapsibleButton.text = "Input"
    self.layout.addWidget(setCollapsibleButton)

    gridLayout = qt.QGridLayout(setCollapsibleButton)
    gridLayout.setSpacing(10)

    labelHostname = qt.QLabel("Hostname: ")
    self.lineEditHostname = qt.QLineEdit()
    labelPort = qt.QLabel("Port Number: ")
    self.lineEditPort = qt.QLineEdit()

    gridLayout.addWidget(labelHostname, 1, 0)
    gridLayout.addWidget(self.lineEditHostname, 1, 1)
    gridLayout.addWidget(labelPort, 1, 2)
    gridLayout.addWidget(self.lineEditPort, 1, 3)

    # Collapsible button - Status
    statusCollapsibleButton = ctk.ctkCollapsibleButton()
    statusCollapsibleButton.text = "Display"
    self.layout.addWidget(statusCollapsibleButton)

    statusGridLayout = qt.QGridLayout(statusCollapsibleButton)
    statusGridLayout.setSpacing(10)

    labelStatus = qt.QLabel("Status: ")
    self.lineEditStatus = qt.QLineEdit()
    labelRegistTime = qt.QLabel("Regist Time: ")
    self.lineEditRegistTime = qt.QLineEdit()

    statusGridLayout.addWidget(labelStatus, 1, 0)
    statusGridLayout.addWidget(self.lineEditStatus, 1, 1)
    statusGridLayout.addWidget(labelRegistTime, 1, 2)
    statusGridLayout.addWidget(self.lineEditRegistTime, 1, 3)

    # Collapsible button - Controller
    controlCollapsibleButton = ctk.ctkCollapsibleButton()
    controlCollapsibleButton.text = "SNRMRRobot Controller"
    self.layout.addWidget(controlCollapsibleButton)

    # Layout within the sample collapsible button
    mainLayout = qt.QVBoxLayout(controlCollapsibleButton)

    controllerFormFrame = qt.QFrame()
    controllerFormLayout = qt.QFormLayout(controllerFormFrame)
    mainLayout.addWidget(controllerFormFrame)
   
    self.buttonConnect = qt.QPushButton("Connect")
    self.buttonConnect.toolTip = "Make connection to the Robot Controller"
    self.buttonRegistration = qt.QPushButton("ZFrameTransform Registration")
    self.buttonSendTarget = qt.QPushButton("Send Target")
    #self.buttonSendTarget.setEnabled(False)
    self.buttonCurrent = qt.QPushButton("Current")
    #self.buttonCurrent.setEnabled(False)
    self.buttonDisconnect = qt.QPushButton("Disconnect")
    #self.buttonDisconnect.setEnabled(False)
    self.buttonReconnect = qt.QPushButton("Reconnect")
    self.buttonReconnect.setEnabled(False)

    controllerFormLayout.addWidget(self.buttonConnect)
    controllerFormLayout.addWidget(self.buttonRegistration)
    controllerFormLayout.addWidget(self.buttonSendTarget)
    controllerFormLayout.addWidget(self.buttonCurrent)
    controllerFormLayout.addWidget(self.buttonDisconnect)
    #controllerFormLayout.addWidget(self.buttonReconnect)

    #
    # input markup fiducial node
    #
    self.targetFiducialsSelector = slicer.qMRMLNodeComboBox()
    self.targetFiducialsSelector.nodeTypes = (("vtkMRMLMarkupsFiducialNode"), "")
    self.targetFiducialsSelector.addEnabled = True
    self.targetFiducialsSelector.removeEnabled = True
    self.targetFiducialsSelector.selectNodeUponCreation = True
    self.targetFiducialsSelector.noneEnabled = False
    self.targetFiducialsSelector.showHidden = False
    self.targetFiducialsSelector.showChildNodeTypes = False
    self.targetFiducialsSelector.setMRMLScene(slicer.mrmlScene)
    controllerFormLayout.addRow("Target: ", self.targetFiducialsSelector)

    self.targetFiducialsNode = None
    self.targetFiducialsSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onFiducialsSelected)

    #
    # target list table
    #
    self.table = qt.QTableWidget(1, 4)
    self.table.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
    self.table.setSelectionMode(qt.QAbstractItemView.SingleSelection)
    
    self.headers = ["Name", "Hole", "Depth(mm)", "Position(RAS)"]
    self.table.setHorizontalHeaderLabels(self.headers)
    self.table.horizontalHeader().setStretchLastSection(True)
    
    mainLayout.addWidget(self.table)

    self.table.connect('cellClicked(int, int)', self.onTableSelected)

    self.onFiducialsSelected()

    # connect of the buttons
    self.buttonConnect.connect('clicked(bool)', self.onButtonConnectClicked)
    self.buttonRegistration.connect('clicked(bool)', self.onButtonRegistrationClicked)
    self.buttonSendTarget.connect('clicked(bool)', self.onButtonSendTargetClicked)
    self.buttonCurrent.connect('clicked(bool)', self.onButtonCurrentClicked)
    self.buttonDisconnect.connect('clicked(bool)', self.onButtonDisconnectClicked)
    self.buttonReconnect.connect('clicked(bool)', self.onButtonReconnectClicked)

    # Add vertical spacer
    self.layout.addStretch(1)


  def onButtonConnectClicked(self):
    if self.connectTag:  # check already has a connect node
      print "Olalalalala!!!"

    else:  # first time to creat the connect node
      self.connectNode = slicer.vtkMRMLIGTLConnectorNode()
      self.connectNode.SetName('testConnectNode')
      slicer.mrmlScene.AddNode(self.connectNode)

      lenHost = len(self.lineEditHostname.text)
      lenPort = len(self.lineEditPort.text)
      # check the input
      if lenHost == 0 or lenPort == 0:
        qt.QMessageBox.information(
          slicer.util.mainWindow(),
          "Slicer Python", "Hostname/Port invalid!")
      else:
        self.strHostname = str(self.lineEditHostname.text)
        self.intPort = int(self.lineEditPort.text)
        self.connectNode.SetTypeClient(self.strHostname, self.intPort)
        self.connectNode.Start()  # connect

        self.activeEvent()  # active the monitor
        self.buttonDisconnect.setEnabled(True)
        self.connectTag = True
    

  def onButtonRegistrationClicked(self):
    if self.registTag:  # check already has a registration data node
      self.connectNode.PushNode(self.dataNodeZFrame)

    else:  # fist time to creat the registration data node
      self.dataNodeZFrame = slicer.vtkMRMLLinearTransformNode()
      self.dataNodeZFrame.SetName("ZFrameTransform")
      slicer.mrmlScene.AddNode(self.dataNodeZFrame)
      self.connectNode.RegisterOutgoingMRMLNode(self.dataNodeZFrame)

      self.connectNode.PushNode(self.dataNodeZFrame)  # send the ZFrameTransform data to controller
      self.registTag = True


  def onButtonSendTargetClicked(self):
    if self.chooseCell == True:
       confirmBox = qt.QMessageBox()
       confirmBox.setText(self.rowStr)
       #confirmBox.setInformativeText(self.rowStr)
       confirmBox.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.Cancel)
       confirmBox.setDefaultButton(qt.QMessageBox.Yes)
       reply = confirmBox.exec_()

       if reply == qt.QMessageBox.Yes:
         print "TargetCellPos: ", self.cellPos
         self.targetCellNode = slicer.vtkMRMLTextNode()
         self.targetCellNode.SetName("TARGETCell")
         self.targetCellNode.SetText(self.cellPos)
         slicer.mrmlScene.AddNode(self.targetCellNode)
         self.connectNode.RegisterOutgoingMRMLNode(self.targetCellNode)
         self.connectNode.PushNode(self.targetCellNode)
  
       elif reply == qt.QMessageBox.Cancel:
         pass
         
    else:
      allTargetBox = qt.QMessageBox()
      allTargetBox.setText("Do you want to send <font color='red'><strong>all the target</strong></font> to the robot?")
      allTargetBox.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.Cancel)
      allTargetBox.setDefaultButton(qt.QMessageBox.Yes)
      replyAll = allTargetBox.exec_()

      if replyAll == qt.QMessageBox.Yes:
        self.currentTargetNode = self.targetFiducialsSelector.currentNode()
        self.connectNode.RegisterOutgoingMRMLNode(self.currentTargetNode)
        self.connectNode.PushNode(self.currentTargetNode)

      elif replyAll == qt.QMessageBox.Cancel:
        pass

  def onButtonCurrentClicked(self):
    self.dataNodeCurrent = slicer.vtkMRMLLinearTransformNode()
    self.dataNodeCurrent.SetName("CURRENT22222")
    slicer.mrmlScene.AddNode(self.dataNodeCurrent)

  def onButtonDisconnectClicked(self):
    self.connectNode.Stop()
    self.lineEditStatus.setText("disconnect")
    self.buttonReconnect.setEnabled(True)
    
  def onButtonReconnectClicked(self):
    pass  # add function

  def activeEvent(self):
    print "into activeEvent"
    self.tempLinearNode = slicer.vtkMRMLLinearTransformNode()
    self.tempLinearNode.SetName('temp')
   
    #self.tagTemp = self.tempLinearNode.AddObserver('ModifiedEvent', self.putInfo)
    #self.tagTemp = self.connectNode.AddObserver('ModifiedEvent', self.putInfo)
    #self.tagTemp = self.connectNode.AddObserver(slicer.vtkMRMLIGTLConnectorNode.ReceiveEvent, self.putInfo)
    #self.tagTemp = self.tempLinearNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.putInfo)
    #self.tagTemp = self.tempLinearNode.AddObserver(self.connectNode.ReceiveEvent, self.putInfo)
    self.tagTemp = self.connectNode.AddObserver(self.connectNode.ReceiveEvent, self.putInfo)
    
    #test
    self.times1 = 0

  def putInfo(self, caller, event):  # caller: vtkMRMLIGTLConnectorNode
    self.times1 = self.times1+1
    #print "********************"
    #print ("into caller", self.times1)

    if caller.IsA('vtkMRMLIGTLConnectorNode'):
      #print "caller is connectNode!"
      nInNode =  caller.GetNumberOfIncomingMRMLNodes()
      #print nInNode
      for i in range(nInNode):  # start from 0
        node = caller.GetIncomingMRMLNode(i) 

        if node.IsA("vtkMRMLLinearTransformNode"):  # lineartransform node              
          if node.GetName() == "feedCurrent":
			pass
        
        elif node.IsA("vtkMRMLTextNode"):  # text node
          if node.GetName() == "feedStatus":
            self.lineEditStatus.setText(node.GetText())
            self.connectNode.UnregisterIncomingMRMLNode(node)

          elif node.GetName() == "feedInfoRegistTime":
            self.lineEditRegistTime.setText(node.GetText())
            qt.QMessageBox.information(
              slicer.util.mainWindow(),
              "Slicer Python", "Registration Accepted!")
            self.connectNode.UnregisterIncomingMRMLNode(node)
            self.buttonSendTarget.setEnabled(True)

          elif node.GetName() == "feedTarget":
            print node.GetText()
            qt.QMessageBox.information(
              slicer.util.mainWindow(),
              "Slicer Python", "Target Accepted!")
            self.connectNode.UnregisterIncomingMRMLNode(node)
            self.buttonCurrent.setEnabled(True)
          
          elif node.GetName() == "feedTargetCell":
            print node.GetText()
            qt.QMessageBox.information(
              slicer.util.mainWindow(),
              "Slicer Python", "Cell Accepted!")
            self.connectNode.UnregisterIncomingMRMLNode(node)
			
        else:  # else to node.IsA
          print "no feedBack!!!!!"
          
        #print i  # start from 0
        #print node.GetID()  # MRML ID
        #print node.GetNodeTagName()  # MRML Type
        #print node.GetClassName() 
        #print node.GetName()
        #print node.IsA('vtkMRMLLinearTransformNode')  # True
        #print "!!!!!!!!!!!!!!!!!!!"

  def onFiducialsSelected(self):
    # Remove observer if previous node exists
    if self.targetFiducialsNode and self.tag:
      self.targetFiducialsNode.RemoveObserver(self.tag)
    
    # Update selected node, add observer, and update control points
    if self.targetFiducialsSelector.currentNode():
      self.targetFiducialsNode = self.targetFiducialsSelector.currentNode()
      self.tag = self.targetFiducialsNode.AddObserver("ModifiedEvent", self.onFiducialsUpdated)
    
    self.updateTable()

  def onFiducialsUpdated(self, caller, event):
    if caller.IsA("vtkMRMLMarkupsFiducialNode") and event == "ModifiedEvent":
      self.updateTable()


  def onTableSelected(self, row, column):
    print "onTableSelected(%d, %d)" %(row, column)
    self.rowNum = row+1
    self.rowStr = "Do you want to send target: <font color='red'><strong>F-" + str(self.rowNum) + " </strong></font>to the robot?"
    
    pos = [0.0, 0.0, 0.0]
    label = self.targetFiducialsNode.GetNthFiducialLabel(row)
    self.targetFiducialsNode.GetNthFiducialPosition(row, pos)
    (indexX, indexY, depth, inRange) = self.logic.computeNearestPath(pos)
    self.cellPos = "%.3f, %.3f, %.3f" %(pos[0], pos[1], pos[2])
    self.chooseCell = True
    
      
  def updateTable(self):
    self.times0 = self.times0 + 1
    print "updateTable: ", self.times0
    
    if not self.targetFiducialsNode:
      self.table.clear()
      self.table.setHorizontalHeaderLabels(self.headers)
    
    else:
      self.tableData = []
      nOfControlPoints = self.targetFiducialsNode.GetNumberOfFiducials()

      if self.table.rowCount != nOfControlPoints:
        self.table.setRowCount(nOfControlPoints)

      for i in range(nOfControlPoints):
        label = self.targetFiducialsNode.GetNthFiducialLabel(i)
      
        pos = [0.0, 0.0, 0.0]
        self.targetFiducialsNode.GetNthFiducialPosition(i, pos)
        (indexX, indexY, depth, inRange) = self.logic.computeNearestPath(pos)

        posStr = "(%.3f, %.3f, %.3f)" %(pos[0], pos[1], pos[2])
        cellLabel = qt.QTableWidgetItem(label)
        cellIndex = qt.QTableWidgetItem("(%s, %s)" %(indexX, indexY))
      
        cellDepth = None
        if inRange:
          cellDepth = qt.QTableWidgetItem("(%.3f)" %depth)
        else:
          cellDepth = qt.QTableWidgetItem("(%.3f)" %depth)
          cellPosition = qt.QTableWidgetItem(posStr)
      
        row = [cellLabel, cellIndex, cellDepth, cellPosition]

        self.table.setItem(i, 0, row[0])
        self.table.setItem(i, 1, row[1])
        self.table.setItem(i, 2, row[2])
        self.table.setItem(i, 3, row[3])
        
        self.tableData.append(row)

    # end the range
    
    # show the table
    self.table.show()
 
   
#
# HelloRobotLogic
#
class HelloRobotLogic:
  def __init__(self):
    self.pathVectors = []
    self.pathOrigins = []

  def computeNearestPath(self, pos):
    p = numpy.array(pos)

    minMag2 = numpy.Inf
    minDepth = 0.0
    minIndex = -1

    i = 0
    for orig in self.pathOrigins:
      vec = self.pathVectors[i]
      op = p - orig
      aproj = numpy.inner(op, vec)
      perp = op-aproj*vec
      mag2 = numpy.vdot(perp, perp)  # magnitude^2
      if mag2 < minMag2:
        minMag2 = mag2
        minIndex = i
        minDepth = aproj
      i = i + 1

    indexX = "--"
    indexY = "--"
    inRange = False
    
    if minIndex >= 0:
        indexX = self.templateIndex[minIndex][0]
        indexY = self.templateIndex[minIndex][1]
        if minDepth > 0 and minDepth < self.templateMaxDepth[minIndex]:
          inRange = True

    return (indexX, indexY, minDepth, inRange)

