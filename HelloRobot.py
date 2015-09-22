import os
import unittest
import csv
import numpy
import math
from decimal import *
from __main__ import vtk, qt, ctk, slicer
#from slicer.ScriptedLoadableModule import *


#
# HelloRobot
#
class HelloRobot():
#class HelloRobot(ScriptedLoadableModule):
  def __init__(self, parent = None):
    #ScriptedLoadableModule.__init__(self, parent)

    parent.title = "Hello Robot"
    parent.categories = ["IGT"]
    parent.dependencies = []
    parent.contributors = ["Yuting Zhao, INPT-ENSEEIHT"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module is to establish the communication connection with the Smart Template Robot device produced by Physical Sciences Inc. and Surgical Planning Laboratory at Brigham and Women's Hospital. This module aslo determines the angulated needle path.
    """
    parent.acknowledgementText = """
    This module was developed by Yuting Zhao(INPT-ENSEEIHT, yuting.zhao@etu.enseeiht.fr). The research is funded by NIH(R41CA192446)
    """ # replace with organization, grant and thanks.
    self.parent = parent


#
# HelloRobotWidget
#
class HelloRobotWidget():
#class HelloRobotWidget(ScriptedLoadableModuleWidget):
  def __init__(self, parent = None):
  #def __init__(self, parent):
    #ScriptedLoadableModuleWidget.setup(self)

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

    self.logic = HelloRobotLogic(None)
    self.generateTag = False

  def setup(self):
    #
    # Collapsible button - Restart 3D Slicer
    #
    restartCollapsibleButton = ctk.ctkCollapsibleButton()
    restartCollapsibleButton.text = "Restart"
    self.layout.addWidget(restartCollapsibleButton)
    restartCollapsibleButton.collapsed = True

    buttonRestart = qt.QPushButton("Restart 3D Slicer")
    buttonRestart.connect('clicked(bool)', self.onButtonRestartClicked)
    restartLayout = qt.QVBoxLayout(restartCollapsibleButton)
    restartLayout.addWidget(buttonRestart)


    #
    # Collapsible button - Configuration
    #
    setCollapsibleButton = ctk.ctkCollapsibleButton()
    setCollapsibleButton.text = "Configuration"
    self.layout.addWidget(setCollapsibleButton)

    configLayout = qt.QVBoxLayout(setCollapsibleButton)
    configFormFrame = qt.QFrame()
    configFormLayout = qt.QFormLayout(configFormFrame)
    configLayout.addWidget(configFormFrame)

    gridLayout = qt.QGridLayout(setCollapsibleButton)
    gridLayout.setSpacing(10)

    labelHostname = qt.QLabel("Hostname: ")
    self.lineEditHostname = qt.QLineEdit()
    self.lineEditHostname.setPlaceholderText("localhost")
    self.lineEditHostname.setFixedWidth(100)
    labelPort = qt.QLabel("Port Number: ")
    self.lineEditPort = qt.QLineEdit()
    self.lineEditPort.setPlaceholderText("18944")
    self.lineEditPort.setFixedWidth(100)

    gridLayout.addWidget(labelHostname, 1, 0)
    gridLayout.addWidget(self.lineEditHostname, 1, 1)
    gridLayout.addWidget(labelPort, 1, 2)
    gridLayout.addWidget(self.lineEditPort, 1, 3)

    configFormLayout.addRow(gridLayout)


    templateConfigPathLayout = qt.QHBoxLayout()
    templateConfigPathLayout.setSpacing(10)
    self.templateConfigPathEdit = qt.QLineEdit()
    settings = qt.QSettings()
    #templateConfigPath = settings.value('HelloRobot/templateConfigFile')
    #if os.path.exists(templateConfigPath):
    #  self.logic.loadTemplateConfigFile2(templateConfigPath)
    #self.templateConfigPathEdit.text = templateConfigPath
    self.templateConfigPathEdit.readOnly = False
    self.templateConfigPathEdit.frame = True
    #self.templateConfigPathEdit.styleSheet = "QLineEdit { background:transparent; }"
    self.templateConfigPathEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)
    templateConfigPathLayout.addWidget(self.templateConfigPathEdit)

    self.templateConfigButton = qt.QPushButton("...")
    self.templateConfigButton.toolTip = "Choose a template configuration file"
    self.templateConfigButton.enabled = True
    self.templateConfigButton.connect('clicked(bool)', self.onTemplateConfigButton)
    templateConfigPathLayout.addWidget(self.templateConfigButton)

    configFormLayout.addRow("Template Config File: ", templateConfigPathLayout)


    #
    # Collapsible button - Robot status
    #
    statusCollapsibleButton = ctk.ctkCollapsibleButton()
    statusCollapsibleButton.text = "SNRMRRobot status"
    self.layout.addWidget(statusCollapsibleButton)

    statusLayout = qt.QHBoxLayout(statusCollapsibleButton)
    statusFormFrame = qt.QFrame()
    statusFormLayout = qt.QFormLayout(statusFormFrame)
    statusLayout.addWidget(statusFormFrame)

    statusGridLayout = qt.QGridLayout(statusCollapsibleButton)
    statusGridLayout.setSpacing(10)

    labelStatus = qt.QLabel("Connection status: ")
    self.lineEditStatus = qt.QLineEdit()
    self.lineEditStatus.setFixedWidth(100)
    labelRegistTime = qt.QLabel("Registration Time: ")
    self.lineEditRegistTime = qt.QLineEdit()
    self.lineEditRegistTime.setFixedWidth(100)
    labelCurrent = qt.QLabel("Current: ")
    self.lineEditCurrent = qt.QLineEdit()

    statusGridLayout.addWidget(labelStatus, 1, 0)
    statusGridLayout.addWidget(self.lineEditStatus, 1, 1)
    statusGridLayout.addWidget(labelRegistTime, 1, 2)
    statusGridLayout.addWidget(self.lineEditRegistTime, 1, 3)
    statusGridLayout.addWidget(labelCurrent, 2, 0)
    statusGridLayout.addWidget(self.lineEditCurrent, 2, 1)


    statusFormLayout.addRow(statusGridLayout)



    #
    # Collapsible button - Controller
    #
    controlCollapsibleButton = ctk.ctkCollapsibleButton()
    controlCollapsibleButton.text = "SNRMRRobot Controller"
    self.layout.addWidget(controlCollapsibleButton)

    mainLayout = qt.QVBoxLayout(controlCollapsibleButton)
    controllerFormFrame = qt.QFrame()
    controllerFormLayout = qt.QFormLayout(controllerFormFrame)
    mainLayout.addWidget(controllerFormFrame)

    controllerGridLayout = qt.QGridLayout(controlCollapsibleButton)
    controllerGridLayout.setSpacing(10)

    lengthButton = 160
    heightButton = 65
    self.buttonConnect = qt.QPushButton("Connect")
    self.buttonConnect.setFixedSize(lengthButton, heightButton)
    self.buttonConnect.toolTip = "Make connection to the Robot Controller"
    self.buttonRegistration = qt.QPushButton("Registration")
    self.buttonRegistration.setFixedSize(lengthButton, heightButton)
    self.buttonSendTarget = qt.QPushButton("Send\n Target")
    self.buttonSendTarget.setFixedSize(lengthButton, heightButton)
    #self.buttonSendTarget.setEnabled(False)
    self.buttonGeneratePath = qt.QPushButton("Generate\n Path")
    self.buttonGeneratePath.setFixedSize(lengthButton, heightButton)
    self.buttonCurrent = qt.QPushButton("Current")
    #self.buttonCurrent.setEnabled(False)
    self.buttonDisconnect = qt.QPushButton("Disconnect")
    self.buttonDisconnect.setFixedSize(lengthButton, heightButton)
    #self.buttonDisconnect.setEnabled(False)
    self.buttonReconnect = qt.QPushButton("Reconnect")
    #self.buttonReconnect.setEnabled(False)


    #controllerFormLayout.addWidget(self.buttonConnect)
    #controllerFormLayout.addWidget(self.buttonRegistration)
    #controllerFormLayout.addWidget(self.buttonGeneratePath)
    #controllerFormLayout.addWidget(self.buttonSendTarget)
    ##controllerFormLayout.addWidget(self.buttonCurrent)
    #controllerFormLayout.addWidget(self.buttonDisconnect)
    ##controllerFormLayout.addWidget(self.buttonReconnect)

    controllerGridLayout.addWidget(self.buttonConnect, 1, 0)
    controllerGridLayout.addWidget(self.buttonRegistration, 1, 1)
    controllerGridLayout.addWidget(self.buttonGeneratePath, 1, 2)
    controllerGridLayout.addWidget(self.buttonSendTarget, 1, 3)
    controllerGridLayout.addWidget(self.buttonDisconnect, 1, 4)

    controllerFormLayout.addRow(controllerGridLayout)

    # connect of the buttons
    self.buttonConnect.connect('clicked(bool)', self.onButtonConnectClicked)
    self.buttonRegistration.connect('clicked(bool)', self.onButtonRegistrationClicked)
    self.buttonGeneratePath.connect('clicked(bool)', self.onButtonGeneratePathClicked)
    self.buttonSendTarget.connect('clicked(bool)', self.onButtonSendTargetClicked)
    self.buttonCurrent.connect('clicked(bool)', self.onButtonCurrentClicked)
    self.buttonDisconnect.connect('clicked(bool)', self.onButtonDisconnectClicked)
    self.buttonReconnect.connect('clicked(bool)', self.onButtonReconnectClicked)


    generatePathLayout = qt.QHBoxLayout()
    self.lineEditNumOfOptionalPath = qt.QLineEdit()
    self.lineEditNumOfOptionalPath.setText("1")
    self.lineEditNumOfOptionalPath.setFixedWidth(30)
    #self.buttonGeneratePath = qt.QPushButton("Generate Path")
    #controllerFormLayout.addWidget(self.buttonGeneratePath)
    #self.buttonGeneratePath.connect('clicked(bool)', self.onButtonGeneratePathClicked)

    generatePathLayout.addWidget(self.lineEditNumOfOptionalPath)
    #generatePathLayout.addWidget(self.buttonGeneratePath)

    controllerFormLayout.addRow("Number of Optional Path: ", generatePathLayout)


    self.showTemplateCheckBox = qt.QCheckBox()
    self.showTemplateCheckBox.checked = 0
    self.showTemplateCheckBox.setToolTip("Show 3D model of the template")
    self.showTemplateCheckBox.connect('toggled(bool)', self.onShowTemplate)
    controllerFormLayout.addRow("Show Template:", self.showTemplateCheckBox)

    self.showOptionalCheckBox = qt.QCheckBox()
    self.showOptionalCheckBox.checked = 0
    self.showOptionalCheckBox.setToolTip("Show 3D model of the needle path")
    self.showOptionalCheckBox.connect('toggled(bool)', self.onShowOptionalPath)
    controllerFormLayout.addRow("Show Optional Path:", self.showOptionalCheckBox)


    #
    # input markup fiducials node
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

    # Add vertical spacer
    self.layout.addStretch(1)


    #
    # path list table
    #
    self.pathTable = qt.QTableWidget(1, 5)
    self.pathTable.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
    self.pathTable.setSelectionMode(qt.QAbstractItemView.SingleSelection)
    self.pathTable.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
    self.headersPathTable = ["Name", "Hole", "Depth(mm)", "Degree", "RAS"]
    self.pathTable.setHorizontalHeaderLabels(self.headersPathTable)
    self.pathTable.horizontalHeader().setStretchLastSection(True)

    mainLayout.addWidget(self.pathTable)

    self.pathTable.connect('cellClicked(int, int)', self.onPathTableSelected)


  def onButtonRestartClicked(self):
    slicer.app.restart()


  def onButtonConnectClicked(self):
    if self.connectTag:  # check already has a connect node
      print "Olalalalala!!!"

    else:  # first time to create the connect node
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
       confirmBox.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.Cancel)
       confirmBox.setDefaultButton(qt.QMessageBox.Yes)
       reply = confirmBox.exec_()

       if reply == qt.QMessageBox.Yes:
         print "TargetCellPos: ", self.cellPos
         self.targetCellNode = slicer.vtkMRMLTextNode()
         self.targetCellNode.SetName("TARGETCell")
         self.targetCellNode.SetText(self.cellPos)
         slicer.mrmlScene.AddNode(self.targetCellNode)

         self.sendPathNode = slicer.vtkMRMLTextNode()
         self.sendPathNode.SetName("SelectPath")
         self.sendPathNode.SetText(str(self.sendPathInfo))
         slicer.mrmlScene.AddNode(self.sendPathNode)

         self.connectNode.RegisterOutgoingMRMLNode(self.targetCellNode)
         self.connectNode.RegisterOutgoingMRMLNode(self.sendPathNode)

         self.connectNode.PushNode(self.targetCellNode)
         self.connectNode.PushNode(self.sendPathNode)

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
    self.lineEditStatus.setStyleSheet("background-color: red")
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
          if node.GetName() == "CURRENT":  # node name the same robot controller part

            if self.receiveCurrentNode == None:
              self.receiveCurrentNode = slicer.vtkMRMLLinearTransformNode()
              self.receiveCurrentNode.SetName("receiveCurrent")
              slicer.mrmlScene.AddNode(self.receiveCurrentNode)

            else:
              mat4x4 = self.receiveCurrentNode.GetMatrixTransformToParent()
              self.matR = mat4x4.GetElement(0, 3)
              self.matA = mat4x4.GetElement(1, 3)
              self.matS = mat4x4.GetElement(2, 3)

              strCurrent = "(%.3f, %.3f, %.3f)" %(self.matR, self.matA, self.matS)
              self.lineEditCurrent.setText(strCurrent)
              self.connectNode.UnregisterIncomingMRMLNode(node)


        elif node.IsA("vtkMRMLTextNode"):  # text node
          if node.GetName() == "feedStatus":
            self.lineEditStatus.setText(node.GetText())
            self.lineEditStatus.setStyleSheet("background-color: green")
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

    if self.generateTag:
      self.logic.hideOptionalPath()


  def onTableSelected(self, row, column):
    print "onTableSelected(%d, %d)" %(row, column)
    self.rowNum = row+1
    #self.rowStr = "Do you want to send target: <font color='red'><strong>F-" + str(self.rowNum) + "</strong></font>to the robot?"

    pos = [0.0, 0.0, 0.0]
    self.selectedTargetLabel = self.targetFiducialsNode.GetNthFiducialLabel(row)
    self.targetFiducialsNode.GetNthFiducialPosition(row, pos)

    print "!!!!!! onTableSelected: ", pos

    (indexX, indexY, depth, inRange) = self.logic.computeNearestPath(pos)

    self.cellPos = "%.3f, %.3f, %.3f" %(pos[0], pos[1], pos[2])
    self.cellPosTarget = (pos[0], pos[1], pos[2])
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

  def onTemplateConfigButton(self):
    path = self.templateConfigPathEdit.text
    path = qt.QFileDialog.getOpenFileName(None, 'Open Template File', path, '*.csv')
    if path is not None and path != "":
      self.templateConfigPathEdit.setText(path)
      settings = qt.QSettings()
      settings.setValue('HelloRobot/templateConfigFile', path)
      # Aug 6, temporary change by ez
      #self.logic.loadTemplateConfigFile(path)
      self.logic.loadTemplateConfigFile2(path)

      self.updateTable()


  def onShowTemplate(self):
    print "onShowTemplate(self)"
    self.logic.setTemplateVisibility(self.showTemplateCheckBox.checked)


  def onShowOptionalPath(self):
    print "onShowOptionalPath()"
    self.logic.setOptionalPathVisibility(self.showOptionalCheckBox.checked)


  def onButtonGeneratePathClicked(self):
    self.generateTag = True

    intNumOfOptionalPath = int(self.lineEditNumOfOptionalPath.text)
    (self.projectPoint, self.depthBase, self.holeInfoList, self.angleList) = self.logic.generatePath(self.cellPosTarget, intNumOfOptionalPath)
    self.pathTableData = []
    getNumberOfPath = len(self.holeInfoList)


    if self.pathTable.rowCount != getNumberOfPath:
      self.pathTable.setRowCount(getNumberOfPath)

    for i in range(getNumberOfPath):
      nthPath = self.holeInfoList[i]

      if nthPath[1] > 150.0:  # max depth = 150mm
        nthPath[1] = Decimal('Infinity')

      indexHole = nthPath[0]

      cellLabel = qt.QTableWidgetItem(self.selectedTargetLabel)
      cellIndex = qt.QTableWidgetItem("(%s, %s)" %(indexHole[0], indexHole[1]))
      cellDepth = qt.QTableWidgetItem("(%.3f)" %nthPath[1])
      cellDegree = qt.QTableWidgetItem("(%.3f)" %self.angleList[i])


      posRAS = "(%.3f, %.3f, %.3f)" %(round(self.cellPosTarget[0], 3), round(self.cellPosTarget[1], 3), round(self.cellPosTarget[2], 3))
      RAS = qt.QTableWidgetItem(posRAS)

      row = [cellLabel, cellIndex, cellDepth, cellDegree, RAS]


      self.pathTable.setItem(i, 0, row[0])
      self.pathTable.setItem(i, 1, row[1])
      self.pathTable.setItem(i, 2, row[2])
      self.pathTable.setItem(i, 3, row[3])
      self.pathTable.setItem(i, 4, row[4])

      self.pathTableData.append(row)

    self.pathTable.show()


  def onPathTableSelected(self, row, column):
    self.pathSelect = self.holeInfoList[row]
    print "pathSelect: ", self.pathSelect

    if self.angleList[row] > 15.0:
      self.rowStr = "Out of range, please choose another needle! :)"

    else:
      self.rowStr = "Do you want to send target: <font color='red'><strong>F-" + str(self.rowNum) + ", (" + self.pathSelect[0][0] + ", " + self.pathSelect[0][1] + ") , Depth: " + str(self.pathSelect[1]) + " " + "Angle: " + str(self.angleList[row]) + " " + "</strong></font>to the robot?"


    insertionPointRAS = self.logic.visualNeedlePath(numpy.array(self.cellPosTarget), self.pathSelect[3])

    #self.sendPathInfo = (hole, array, depth, degree)
    #self.sendPathInfo = ((self.pathSelect[0][0], self.pathSelect[0][1]), insertionPointRAS, self.pathSelect[1], self.angleList[row])
    self.sendPathInfo = (self.pathSelect[0][0], self.pathSelect[0][1], self.pathSelect[1], self.angleList[row])

    print "self.sendPathInfo: ", self.sendPathInfo  #(('F', ' "0"'), array([  0.,   0.,  30.]), 67.125, 0.886)


# ----------------------------------------------------------------------------------------------------------------
# HelloRobotLogic
#
class HelloRobotLogic():
#class HelloRobotLogic(ScriptedLoadableModuleLogic):
  def __init__(self, parent = None):
  #def __init__(self, parent):
    #ScriptedLoadableModuleLogic.__init__(self, parent)

    self.pathVectors = []
    self.pathOrigins = []
    self.templateModelNodeID = ''
    self.needlePathModelNodeID = ''
    self.optionalPathModelNodeID = ''
    self.selectNeedleNodeID = ''

    self.templateMaxDepth = []
    self.templatePathOrigins = []  ## Origins of needle paths
    self.templatePathVectors = []  ## Normal vectors of needle paths
    self.pathOrigins = []  ## Origins of needle paths (after transformation by parent transform node)
    self.pathVectors = []  ## Normal vectors of needle paths (after transformation by parent transform node)

    self.generateTag = False


  def loadTemplateConfigFile2(self, path):
    print "loadTemplateConfigFil2"
    self.templateIndex = []
    self.templateConfig = []
    self.templateInRAS = []
    self.templateOutRAS = []

    header = False
    reader = csv.reader(open(path, 'rb'))
    try:
      for column in reader:
        if header:
          self.templateIndex.append(column[0:2])
          self.templateConfig.append([float(column[2]), float(column[3]), float(column[4]),
                                      float(column[5]), float(column[6]), float(column[7]),
                                      float(column[8])])

          self.templateInRAS.append([float(column[2]), float(column[3]), float(column[4])])
          self.templateOutRAS.append([float(column[5]), float(column[6]), float(column[7])])

        else:
          self.templateName = column[0]
          header = True
    except csv.Error as e:
      print('file %s, line %d: %s' % (filename, reader.line_num, e))

    self.createTemplateModel()
    self.setTemplateVisibility(0)
    self.updateTemplateVectors()
    self.setOptionalPathVisibility(0)


#----------------------------------------------------------------------------------------------------------------
  def createTemplateModel(self):
    self.templatePathVectors = []
    self.templatePathOrigins = []

    tempModelNode = slicer.mrmlScene.GetNodeByID(self.templateModelNodeID)
    if tempModelNode == None:
      tempModelNode = slicer.vtkMRMLModelNode()
      tempModelNode.SetName('NeedleGuideTemplate')
      slicer.mrmlScene.AddNode(tempModelNode)
      self.templateModelNodeID = tempModelNode.GetID()

      dnode = slicer.vtkMRMLModelDisplayNode()
      slicer.mrmlScene.AddNode(dnode)
      tempModelNode.SetAndObserveDisplayNodeID(dnode.GetID())
      self.modelNodetag = tempModelNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent,
                                                    self.onTemplateTransformUpdated)

    tempModelAppend = vtk.vtkAppendPolyData()

    for row in self.templateConfig:
      p1 = numpy.array(row[0:3])
      p2 = numpy.array(row[3:6])

      tempLineSource = vtk.vtkLineSource()
      tempLineSource.SetPoint1(p1)
      tempLineSource.SetPoint2(p2)

      tempTubeFilter = vtk.vtkTubeFilter()
      tempTubeFilter.SetInputConnection(tempLineSource.GetOutputPort())
      tempTubeFilter.SetRadius(1.0)
      tempTubeFilter.SetNumberOfSides(18)
      tempTubeFilter.CappingOn()
      tempTubeFilter.Update()

      pathLineSource = vtk.vtkLineSource()
      v = p2-p1
      nl = numpy.linalg.norm(v)
      n = v/nl  # normal vector
      l = row[6]
      p3 = p1 + l * n
      pathLineSource.SetPoint1(p1)
      pathLineSource.SetPoint2(p3)

      self.templatePathOrigins.append([row[0], row[1], row[2], 1.0])
      self.templatePathVectors.append([n[0], n[1], n[2], 1.0])
      self.templateMaxDepth.append(row[6])

      pathTubeFilter = vtk.vtkTubeFilter()
      pathTubeFilter.SetInputConnection(pathLineSource.GetOutputPort())
      pathTubeFilter.SetRadius(0.8)
      pathTubeFilter.SetNumberOfSides(18)
      pathTubeFilter.CappingOn()
      pathTubeFilter.Update()

      if vtk.VTK_MAJOR_VERSION <= 5:
        tempModelAppend.AddInput(tempTubeFilter.GetOutput())
#        pathModelAppend.AddInput(pathTubeFilter.GetOutput())
      else:
        tempModelAppend.AddInputData(tempTubeFilter.GetOutput())
#        pathModelAppend.AddInputData(pathTubeFilter.GetOutput())

      tempModelAppend.Update()
      tempModelNode.SetAndObservePolyData(tempModelAppend.GetOutput())
#      pathModelAppend.Update()
#      pathModelNode.SetAndObservePolyData(pathModelAppend.GetOutput())


  def setModelVisibilityByID(self, id, visible):
    mnode = slicer.mrmlScene.GetNodeByID(id)
    if mnode != None:
      dnode = mnode.GetDisplayNode()
      if dnode != None:
        dnode.SetVisibility(visible)


  def setModelSliceIntersectionVisibilityByID(self, id, visible):
    mnode = slicer.mrmlScene.GetNodeByID(id)
    if mnode != None:
      dnode = mnode.GetDisplayNode()
      if dnode != None:
        dnode.SetSliceIntersectionVisibility(visible)


  def setTemplateVisibility(self, visibility):
    self.setModelVisibilityByID(self.templateModelNodeID, visibility)


  def setOptionalPathVisibility(self, visibility):
    print "setOptionalPathVisibility: ", visibility

    self.setModelVisibilityByID(self.optionalPathModelNodeID, visibility)
    self.setModelSliceIntersectionVisibilityByID(self.optionalPathModelNodeID, visibility)


  def onTemplateTransformUpdated(self,caller,event):
    print 'onTemplateTransformUpdated()'
    self.updateTemplateVectors()


  def updateTemplateVectors(self):
    print 'updateTemplateVectors()'

    mnode = slicer.mrmlScene.GetNodeByID(self.templateModelNodeID)
    if mnode == None:
      return 0
    tnode = mnode.GetParentTransformNode()

    trans = vtk.vtkMatrix4x4()
    if tnode != None:
      tnode.GetMatrixTransformToWorld(trans);
    else:
      trans.Identity()

    # Calculate offset
    zero = [0.0, 0.0, 0.0, 1.0]
    offset = []
    offset = trans.MultiplyDoublePoint(zero)

    self.pathOrigins = []
    self.pathVectors = []

    i = 0
    for orig in self.templatePathOrigins:
      torig = trans.MultiplyDoublePoint(orig)
      self.pathOrigins.append(numpy.array(torig[0:3]))
      vec = self.templatePathVectors[i]
      tvec = trans.MultiplyDoublePoint(vec)
      self.pathVectors.append(numpy.array([tvec[0]-offset[0], tvec[1]-offset[1], tvec[2]-offset[2]]))
      i = i + 1


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


# ----------------------------------------------------------------------------------------------------------------
  def generatePath(self, cellPos, intNumOfOptionalPath):
    pos = numpy.array(cellPos)

    print "generatePath() called"
    print "pos: ", (round(pos[0], 3), round(pos[1], 3), round(pos[2], 3))

    # TODO: should randomly choose 3 points on the template (!!! same line situation)
    template = self.determineTemplatePlane(self.pathOrigins[0], self.pathOrigins[129], self.pathOrigins[200])
    print "template: ", template

    pPoint = self.projectPoint(pos, template)
    print "projectPoint: ", (round(pPoint[0],3), round(pPoint[1],3), round(pPoint[2],3))

    depthBase = self.disPoint2Plane(pos, template)
    print "depthBase: ", round(depthBase, 3)

    [xDisHList, xDisSList] = self.insertionPathsDistance(intNumOfOptionalPath)

    disList = self.disPoint2Holes(pos, self.pathOrigins)

    holeInfoList = self.closestPath(pos, xDisSList, disList, self.pathOrigins)
    print "holeInfoList: ", holeInfoList  #[[['F', ' "-3"'], 61.482, 0.0, 79]]

    angleList = self.determineAngle(depthBase, holeInfoList)

    self.createOptionalPathModel(pos, holeInfoList, intNumOfOptionalPath)

    return (pPoint, depthBase, holeInfoList, angleList)


  def determineTemplatePlane(self, point1, point2, point3):
    print "determineTemplatePlane()"
    point1R = point1[0]
    point1A = point1[1]
    point1S = point1[2]

    point2R = point2[0]
    point2A = point2[1]
    point2S = point2[2]

    point3R = point3[0]
    point3A = point3[1]
    point3S = point3[2]

    self.planeA = (point2A-point1A) * (point3S-point1S) - (point3A-point1A)*(point2S-point1S)
    self.planeB = (point2S-point1S) * (point3R-point1R) - (point3S-point1S)*(point2R-point1R)
    self.planeC = (point2R-point1R) * (point3A-point1A) - (point3R-point1R)*(point2A-point1A)
    self.planeD = -self.planeA*point1R - self.planeB*point1A - self.planeC*point1S

    self.templatePlane = numpy.array([self.planeA, self.planeB, self.planeC, self.planeD])

    return self.templatePlane


  def projectPoint(self, pointArray, planeArray):
    print "projectPoint()"
    # k = -(ax+by+cz+d)/(aa+bb+cc)
    # x' = x+ka
    k = -float((planeArray[0]*pointArray[0] + planeArray[1]*pointArray[1] + planeArray[2]*pointArray[2] + planeArray[3]))/float((planeArray[0]**2 + planeArray[1]**2 + planeArray[2]**2))

    proj_R = pointArray[0] + k*planeArray[0]
    proj_A = pointArray[1] + k*planeArray[1]
    proj_S = pointArray[2] + k*planeArray[2]
    projectPointOnPlane = [proj_R, proj_A, proj_S]
    return projectPointOnPlane  # in format [R,A,S]


  def disPoint2Plane(self, pos, templatePlane):
    #print "disPoint2Plane()"

    numer = math.fabs(templatePlane[0]*pos[0] + templatePlane[1]*pos[1] + templatePlane[2]*pos[2] + templatePlane[3])
    denom = math.sqrt(pow(templatePlane[0],2) + pow(templatePlane[1],2) + pow(templatePlane[2],2))
    self.depthNeedleBase = float(numer)/float(denom)

    return self.depthNeedleBase


  def insertionPathsDistance(self, numOfPath):
    print "insertionPathDistance()"

    x_disH_list = []
    x_disS_list = []
    self.x_degree_list = []
    self.disVLimit = self.depthNeedleBase

    if numOfPath == 1:
      x_disH_0 = math.tan((0.0*math.pi)/180)*self.disVLimit
      x_disS_0 = float(self.disVLimit)/math.cos((0.0*math.pi)/180)
      x_disH_list.append(x_disH_0)
      x_disS_list.append(x_disS_0)
      self.x_degree_list.append(0)

    else:
      gap = float(15)/(numOfPath-1)

      for x in numpy.arange(0, 15, gap):
        x_disH = math.tan((x*math.pi)/180)*self.disVLimit
        x_disS = float(self.disVLimit)/math.cos((x*math.pi)/180)

        x_disH_list.append(x_disH)
        x_disS_list.append(x_disS)
        self.x_degree_list.append(x)

      # the limitation -- 15 degree
      x_disH_15 = math.tan((15*math.pi)/180)*self.disVLimit
      x_disS_15 = float(self.disVLimit)/math.cos((15*math.pi)/180)
      x_disH_list.append(x_disH_15)
      x_disS_list.append(x_disS_15)
      self.x_degree_list.append(15)

    return x_disH_list, x_disS_list


  def dis2Points(self, point1, point2):
    #print "dis2Points()"
    temp = [point1[0]-point2[0], point1[1]-point2[1], point1[2]-point2[2]]
    dis = (temp[0]**2 + temp[1]**2 + temp[2]**2)**0.5
    return dis


  def disPoint2Holes(self, pos, templateRAS):
    print "disPoint2Holes()"

    dis_list = []
    for holePoint in templateRAS:
      dis = self.dis2Points(pos, holePoint)
      dis_list.append(dis)
    return dis_list


  def closestPath(self, pos, x_disS_list, dis_list, templateRAS):
    print "closestPath()"
    lenDisList = len(dis_list)
    self.minLocationIndexList = []
    self.holeInfoList = []
    self.templateRAS = templateRAS
    j = 0

    print "x_disS_list: ", x_disS_list
    print "len(x_disS_list): ", len(x_disS_list)

    for optionalPath in x_disS_list:
      print "optionalPath: ", optionalPath
      subList = []
      tempPath = [optionalPath]*lenDisList
      #subList = [math.fabs(ideal - fact for ideal,fact in zip(tempPath, dis_list))]

      for i in range(lenDisList):
        closestTemp = math.fabs(tempPath[i] - dis_list[i])
        subList.append(closestTemp)
        #i = i+1

      self.minLocationIndex = subList.index(min(subList))
      self.minLocationIndexList.append(self.minLocationIndex)  # size as the numberOfPath

      self.disReal = self.dis2Points(pos, self.pathOrigins[self.minLocationIndex])  # TODO: disReal should include orientation information & couldn't over max depth 150


      self.holeInfoList.append([self.templateIndex[self.minLocationIndex], round(self.disReal,3), round(self.x_degree_list[j],3), self.minLocationIndex])
      j = j+1

      #print "minLocationIndex: ", self.minLocationIndex
      #print "self.templateIndex[self.minLocationIndex]: ", self.templateIndex[self.minLocationIndex]
      #print "templateRAS[self.minLocationIndex]: ", self.templateRAS[self.minLocationIndex]

      #self.visualNeedlePath(pos, self.templateRAS[self.minLocationIndex])

    return self.holeInfoList


  def visualNeedlePath(self, pos, pointOnTemplateRAS):
    if type(pointOnTemplateRAS) == list:
      pass
    elif type(pointOnTemplateRAS) == int:
      pointOnTemplateRAS = self.templateRAS[pointOnTemplateRAS]

    self.pathModelNode = slicer.mrmlScene.GetNodeByID(self.needlePathModelNodeID)
    if self.pathModelNode == None:
      self.pathModelNode = slicer.vtkMRMLModelNode()
      self.pathModelNode.SetName('AngulatedNeedlePath')
      slicer.mrmlScene.AddNode(self.pathModelNode)
      self.needlePathModelNodeID = self.pathModelNode.GetID()

      self.dnodeSelectedPath = slicer.vtkMRMLModelDisplayNode()
      self.dnodeSelectedPath.SetColor(0, 1, 1)
      slicer.mrmlScene.AddNode(self.dnodeSelectedPath)
      self.pathModelNode.SetAndObserveDisplayNodeID(self.dnodeSelectedPath.GetID())

    pathModelAppend = vtk.vtkAppendPolyData()

    tempLineSource = vtk.vtkLineSource()
    tempLineSource.SetPoint1(pos)  # target in RAS
    tempLineSource.SetPoint2(pointOnTemplateRAS)  # point on template in RAS

    tempTubeFilter = vtk.vtkTubeFilter()
    tempTubeFilter.SetInputConnection(tempLineSource.GetOutputPort())
    tempTubeFilter.SetRadius(1.0)
    tempTubeFilter.SetNumberOfSides(18)
    tempTubeFilter.CappingOn()
    tempTubeFilter.Update()

    self.setModelSliceIntersectionVisibilityByID(self.needlePathModelNodeID, 1)

    if vtk.VTK_MAJOR_VERSION <= 5:
      pathModelAppend.AddInput(tempTubeFilter.GetOutput())
    else:
      pathModelAppend.AddInputData(tempTubeFilter.GetOutput())

    pathModelAppend.Update()
    self.pathModelNode.SetAndObservePolyData(pathModelAppend.GetOutput())


    #
    # Reslice along with the selected needle
    #

    print "(target) pos: ", pos
    print "pointOnTemplateRAS: ", pointOnTemplateRAS

    R = pointOnTemplateRAS[0]
    A = pointOnTemplateRAS[1]
    S = pointOnTemplateRAS[2]

    deltaR = pos[0] - R
    deltaA = pos[1] - A
    deltaS = pos[2] - S

    pathVector = numpy.array([deltaR, deltaA, deltaS])
    tR = numpy.array([1.0, 0, 0])

    vectorA = numpy.cross(pathVector, tR)
    vectorS = numpy.cross(pathVector, vectorA)


    pathVectorNorm = numpy.linalg.norm(pathVector)
    vectorANorm = numpy.linalg.norm(vectorA)
    vectorSNorm = numpy.linalg.norm(vectorS)

    matrix = vtk.vtkMatrix4x4()
    matrix.Identity()

    ## TODO: if pathVector is parallel to R
    matrix.SetElement(0, 0, pathVector[0]/pathVectorNorm)
    matrix.SetElement(1, 0, pathVector[1]/pathVectorNorm)
    matrix.SetElement(2, 0, pathVector[2]/pathVectorNorm)

    matrix.SetElement(0, 1, vectorA[0]/vectorANorm)
    matrix.SetElement(1, 1, vectorA[1]/vectorANorm)
    matrix.SetElement(2, 1, vectorA[2]/vectorANorm)

    matrix.SetElement(0, 2, vectorS[0]/vectorSNorm)
    matrix.SetElement(1, 2, vectorS[1]/vectorSNorm)
    matrix.SetElement(2, 2, vectorS[2]/vectorSNorm)

    matrix.SetElement(0, 3, R)
    matrix.SetElement(1, 3, A)
    matrix.SetElement(2, 3, S)


    selectNeedleNode = slicer.mrmlScene.GetNodeByID(self.selectNeedleNodeID)
    if selectNeedleNode == None:
      selectNeedleNode = slicer.vtkMRMLLinearTransformNode()
      selectNeedleNode.SetName('SelectedNeedle')
      slicer.mrmlScene.AddNode(selectNeedleNode)
      self.selectNeedleNodeID = selectNeedleNode.GetID()

    selectNeedleNode.SetAndObserveMatrixTransformToParent(matrix)

    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for index in range(modelNodes.GetNumberOfItems()):
      indexNode = modelNodes.GetItemAsObject(index)
      if indexNode.GetTransformNodeID() == selectNeedleNode.GetID():
        indexNode.SetDisplayVisibility(1)
        self.selectNeedleModelNode = indexNode
        print indexNode.GetID()

    red = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
    yellow = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
    green = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")

    vrdLogic = slicer.modules.volumereslicedriver.logic()
    redDriver = vrdLogic.SetDriverForSlice(selectNeedleNode.GetID(), red)
    redMode = vrdLogic.SetModeForSlice(vrdLogic.MODE_INPLANE, red)
    yellowDriver = vrdLogic.SetDriverForSlice(selectNeedleNode.GetID(), yellow)
    yellowMode = vrdLogic.SetModeForSlice(vrdLogic.MODE_INPLANE90, yellow)
    greenDriver = vrdLogic.SetDriverForSlice(selectNeedleNode.GetID(), green)
    greenMode = vrdLogic.SetModeForSlice(vrdLogic.MODE_TRANSVERSE, green)
    vrdLogic.Modified()

    return pointOnTemplateRAS


  def createOptionalPathModel(self, pos, holeInfoList, intNumOfOptionalPath):
    if intNumOfOptionalPath == 1:
      self.setOptionalPathVisibility(1)

    pathListRAS = []

    for i in range(len(holeInfoList)):
      pathListRAS.append(self.templateRAS[holeInfoList[i][3]])

    print "pathListRAS: ", pathListRAS

    #(not generate path -> pass, otherwise go on)

    self.optModelNode = slicer.mrmlScene.GetNodeByID(self.optionalPathModelNodeID)
    if self.optModelNode == None:
      self.optModelNode = slicer.vtkMRMLModelNode()
      self.optModelNode.SetName('AllOptionalPaths')
      slicer.mrmlScene.AddNode(self.optModelNode)
      self.optionalPathModelNodeID = self.optModelNode.GetID()

      self.dnodeOpt = slicer.vtkMRMLModelDisplayNode()
      self.dnodeOpt.SetColor(0.96,0.92,0.56)
      slicer.mrmlScene.AddNode(self.dnodeOpt)
      self.optModelNode.SetAndObserveDisplayNodeID(self.dnodeOpt.GetID())

    optModelAppend = vtk.vtkAppendPolyData()

    #for path in pathListRAS:
    for index in range(len(pathListRAS)):
      optLineSource = vtk.vtkLineSource()
      optLineSource.SetPoint1(pos)
      optLineSource.SetPoint2(pathListRAS[index])

      optTubeFilter = vtk.vtkTubeFilter()
      optTubeFilter.SetInputConnection(optLineSource.GetOutputPort())
      optTubeFilter.SetRadius(1.0)
      optTubeFilter.SetNumberOfSides(10)
      optTubeFilter.CappingOn()
      optTubeFilter.Update()

      if vtk.VTK_MAJOR_VERSION <= 5:
        optModelAppend.AddInput(optTubeFilter.GetOutput())
      else:
        optModelAppend.AddInputData(optTubeFilter.GetOutput())

      optModelAppend.Update()
      self.optModelNode.SetAndObservePolyData(optModelAppend.GetOutput())


  def hideOptionalPath(self):
    slicer.mrmlScene.RemoveNode(self.optModelNode)
    slicer.mrmlScene.RemoveNode(self.dnodeOpt)

    if self.pathModelNode:
      slicer.mrmlScene.RemoveNode(self.pathModelNode)
      slicer.mrmlScene.RemoveNode(self.dnodeSelectedPath)


  def determineAngle(self, depthBase, holeInfoList):
    alphaList = []

    for item in holeInfoList:
      disSlop = item[1]
      alpha_radians = math.asin(float(depthBase/disSlop))
      alpha_degree = round(90-(180*alpha_radians/math.pi),3)
      if alpha_degree > 15.0:
        alpha_degree = Decimal('Infinity')

      alphaList.append(alpha_degree)

    return alphaList


