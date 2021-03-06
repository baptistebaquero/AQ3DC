import os
import unittest
import logging
# import patsy
import vtk, qt, ctk, slicer
import glob
import numpy as np
import collections
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# AQ3DC
#
try:
  import pandas as pd
  import PyQt5

except: 
  slicer.util.pip_install('pandas')
  slicer.util.pip_install('PyQt5')
  import pandas as pd
  from PyQt5.QtCore import QObject,QModelIndex,QVariant

def ReadFolder(landmarks_dir_T1,landmarks_dir_T2):
  dic_patient = {} 
  dic_time = {}
  dic_tooth = {}

  landmarks_normpath_T1 = os.path.normpath("/".join([landmarks_dir_T1,'**','']))
  landmarks_normpath_T2 = os.path.normpath("/".join([landmarks_dir_T2,'**','']))
  lst_landmarks_dir = [landmarks_normpath_T1,landmarks_normpath_T2]

  for land_dir in lst_landmarks_dir:
      for jsonfile in sorted(glob.iglob(land_dir, recursive=True)):
          if os.path.isfile(jsonfile) and True in [ext in jsonfile for ext in [".json"]]:
            num_patient= os.path.basename(jsonfile).split("_")[0]
            time = os.path.basename(jsonfile).split("_")[1]
            if "_mand_" or "_L" in jsonfile:
              if num_patient in dic_patient.keys():
                if time in dic_time.keys():
                  dic_time[time]['path_landmark_L'] = jsonfile
                  dic_patient[num_patient] = dic_time
                else :
                  dic_time[time] = {'path_landmark_L' : jsonfile}
                  dic_patient[num_patient] = dic_time
              else:
                dic_time[time] = {'path_landmark_L' : jsonfile}
                dic_patient[num_patient] = dic_time
            else :
              if num_patient in dic_patient.keys():
                if time in dic_time.keys():
                  dic_time[time]['path_landmark_U'] = jsonfile
                  dic_patient[num_patient] = dic_time
                else :
                  dic_time[time] = {'path_landmark_U' : jsonfile}
                  dic_patient[num_patient] = dic_time
              else:
                dic_time[time] = {'path_landmark_U' : jsonfile}
                dic_patient[num_patient] = dic_time
  
  # print(dic_patient)
  for obj in dic_patient.items():
    obj=obj[1]    
    for patient_t in obj.items():
      time = patient_t[0]
      dic_path_patient = patient_t[1]
      # print(dic_path_patient)
      # print(dic_path_patient.items())
      for path_patient in dic_path_patient.items():
        # print(path_patient)
        json_file = pd.read_json(path_patient[1])
        markups = json_file.loc[0,'markups']
        controlPoints = markups['controlPoints']
        for i in range(len(controlPoints)):
          label = controlPoints[i]["label"]#.split("-")[1]
          tooth = label[:3]
          type_land = label[3:]
          position = controlPoints[i]["position"]
          if tooth not in dic_tooth.keys():
            dic_tooth[tooth] = {}
          if type_land not in dic_tooth[tooth]:
            dic_tooth[tooth][type_land] = {}
          
          dic_tooth[tooth][type_land][time] = position
  # print(dic_tooth)
  return dic_tooth

DistanceResult = collections.namedtuple("DistanceResult", ("delta", "norm"))
def computeDistance(point1, point2) -> DistanceResult:
    delta = np.abs(np.subtract(point2,point1))
    return DistanceResult(
        delta,
        np.linalg.norm(delta),
    )

def compute_distance_T1T2(dic_tooth,type):
  dic_distance = {}
  for landmark in dic_tooth.items():
    land = landmark[1]
    name = landmark[0]
    point_T1 = np.array(land[type]['T1'])
    point_T2 = np.array(land[type]['T2'])
    distance = computeDistance(point_T2,point_T1)
    if name not in dic_distance.keys(): 
      dic_distance[name] = {}
    dic_distance[name] = distance
  print(dic_distance)
  return dic_distance



# def export_csv(dic_distance):
#   p


class AQ3DC(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "AQ3DC"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#AQ3DC">module documentation</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # AQ3DC1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='AQ3DC',
    sampleName='AQ3DC1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'AQ3DC1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='AQ3DC1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='AQ3DC1'
  )

  # AQ3DC2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='AQ3DC',
    sampleName='AQ3DC2',
    thumbnailFileName=os.path.join(iconsPath, 'AQ3DC2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='AQ3DC2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='AQ3DC2'
  )
  

#
# AQ3DCWidget
#

class AQ3DCWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/AQ3DC.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = AQ3DCLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
    # self.deps = DependantMarkups.DependantMarkupsLogic 


    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    # self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    # self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    # self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    # self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
    # self.ui.invertedOutputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)


    self.lm_tab = LMTab()
    self.ui.verticalLayout_1.addWidget(self.lm_tab.widget)

    self.table_view = TableView()
    self.ui.verticalLayout_2.addWidget(self.lm_tab.widget)

    

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.pushButton_DataFolder_T1.connect('clicked(bool)',self.onSearchFolderButton_T1)
    self.ui.pushButton_DataFolder_T2.connect('clicked(bool)',self.onSearchFolderButton_T2)
    self.ui.pushButton_Display.connect('clicked(bool)',self.onDisplayButton)
    self.ui.pushButton_OclusalDataT1T2.connect('clicked(bool)',self.onComputeOclusalDistance)
    self.ui.pushButton_MesialDataT1T2.connect('clicked(bool)',self.onComputeMesialDistance)
    self.ui.pushButton_DistalDataT1T2.connect('clicked(bool)',self.onComputeDistalDistance)
    # self.ui.pushButton_Run.connect('clicked(bool)',self.onRun)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

    self.surface_folder = '/home/luciacev-admin/Desktop/AQ3DC_data/renamed_data/T1'
    self.surface_folder_2 = '/home/luciacev-admin/Desktop/AQ3DC_data/renamed_data/T2'
    self.dic_tooth = ReadFolder(self.surface_folder,self.surface_folder_2)
    print(self.dic_tooth)

    

  def onSearchFolderButton_T1(self):
    surface_folder = qt.QFileDialog.getExistingDirectory(self.parent, "Select a scan folder")
    if surface_folder != '':
      self.surface_folder = surface_folder
      self.ui.lineEditLandPathT1.setText(self.surface_folder)
  
  def onSearchFolderButton_T2(self):
    surface_folder = qt.QFileDialog.getExistingDirectory(self.parent, "Select a scan folder")
    if surface_folder != '':
      self.surface_folder_2 = surface_folder
      self.ui.lineEditLandPathT2.setText(self.surface_folder_2)

  def onDisplayButton(self):
    # self.dic_tooth = ReadFolder(self.surface_folder,self.surface_folder_2)
    self.lm_tab.Clear()
    self.lm_tab.FillTab(self.dic_tooth)
    # self.table_view.create_tab()

  def onComputeOclusalDistance(self):   
    lst_select_tooth = self.lm_tab.Get_selected_tooth()
    print(lst_select_tooth)
    self.update_dic_tooth = self.dic_tooth.copy()
    for tooth in self.dic_tooth:
      if tooth not in lst_select_tooth:
        self.update_dic_tooth.pop(tooth)

    self.dic_distance = compute_distance_T1T2(self.update_dic_tooth,'o')

  def onComputeMesialDistance(self): 
    lst_select_tooth = self.lm_tab.Get_selected_tooth()
    print(lst_select_tooth)
    self.update_dic_tooth = self.dic_tooth.copy()
    for tooth in self.dic_tooth:
      if tooth not in lst_select_tooth:
        self.update_dic_tooth.pop(tooth)
    
    self.dic_distance = compute_distance_T1T2(self.update_dic_tooth,'m')
  
  def onComputeDistalDistance(self):
    lst_select_tooth = self.lm_tab.Get_selected_tooth()
    print(lst_select_tooth)
    self.update_dic_tooth = self.dic_tooth.copy()
    for tooth in self.dic_tooth:
      if tooth not in lst_select_tooth:
        self.update_dic_tooth.pop(tooth)
    
    self.dic_distance = compute_distance_T1T2(self.update_dic_tooth,'d')

  def onExportButton(self):
    self.logic.exportationFunction(
      self.directoryExportDistance,
      self.filenameExportDistance,
      self.distance_table,
      "distance",
    )


  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    # self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    # self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    # self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
    # self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    # self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
      self.ui.applyButton.toolTip = "Compute output volume"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output volume nodes"
      self.ui.applyButton.enabled = False

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
    self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)

    self._parameterNode.EndModify(wasModified)


  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:

      # Compute output
      self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
        self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)

      # Compute inverted output (if needed)
      if self.ui.invertedOutputSelector.currentNode():
        # If additional output volume is selected then result with inverted threshold is written there
        self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
          self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)

    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()

class LMTab:
  def __init__(self) -> None:

    self.widget = qt.QWidget()
    layout = qt.QVBoxLayout(self.widget)

    self.LM_tab_widget = qt.QTabWidget()
    self.LM_tab_widget.minimumSize = qt.QSize(100,200)
    self.LM_tab_widget.maximumSize = qt.QSize(800,400)
    self.LM_tab_widget.setMovable(True)


    # print(self.lm_status_dic)
    # print(lcbd)
    buttons_wid = qt.QWidget()
    buttons_layout = qt.QHBoxLayout(buttons_wid)
    self.select_all_btn = qt.QPushButton("Select All")
    self.select_all_btn.setEnabled(False)
    self.select_all_btn.connect('clicked(bool)', self.SelectAll)
    self.clear_all_btn = qt.QPushButton("Clear All")
    self.clear_all_btn.setEnabled(False)
    self.clear_all_btn.connect('clicked(bool)', self.ClearAll)

    buttons_layout.addWidget(self.select_all_btn)
    buttons_layout.addWidget(self.clear_all_btn)

    layout.addWidget(self.LM_tab_widget)
    layout.addWidget(buttons_wid)
    self.lm_status_dic = {}

  def Clear(self):
    self.LM_tab_widget.clear()

  def FillTab(self,lm_dic):
    self.select_all_btn.setEnabled(True)
    self.clear_all_btn.setEnabled(True)

    self.lm_group_dic = lm_dic
    print(self.lm_group_dic)
    # self.lm_group_dic["All"] = []
   
    lm_lst=[]
    lm_type_lst=[]
    lst_wid=[]
    lst_wtype=[]
    self.lm_status_dic = {}
    self.check_box_dic = {}

    for landmark_name,type_land_dic in lm_dic.items():
        lm_lst.append(landmark_name)
        for type,time_dic in type_land_dic.items():
          if type not in lm_type_lst:
            lm_type_lst.append(type)

    for lm in lm_lst:
      new_cb = qt.QCheckBox(lm)
      self.check_box_dic[new_cb] = lm
      lst_wid.append(new_cb)
      if lm not in self.lm_status_dic.keys():
          self.lm_status_dic[lm] = False

    for type in lm_type_lst:
      new_cb = qt.QCheckBox(type)
      lst_wtype.append(new_cb)

    new_tooth_tab = self.GenNewTab(lst_wid)
    new_lm_type_tab = self.GenNewTab(lst_wtype)

    self.LM_tab_widget.insertTab(0,new_tooth_tab,'tooth')
    self.LM_tab_widget.insertTab(-1,new_lm_type_tab,'landmarks type')
     
    self.LM_tab_widget.currentIndex = 0

    # print(self.check_box_dic)
    lcbd = {}
    for cb,lm in self.check_box_dic.items():
      if lm not in lcbd.keys():
        lcbd[lm] = [cb]
      else:
        lcbd[lm].append(cb)

    self.lm_cb_dic = lcbd

    for cb in self.check_box_dic.keys():
      cb.connect("toggled(bool)", self.CheckBox)

  def CheckBox(self, caller=None, event=None):
    print(self.check_box_dic)
    for cb,lm in self.check_box_dic.items():
      if cb.checkState():
        state = True
      else:
        state = False
      
      if self.lm_status_dic[lm] != state:
        self.UpdateLmSelect(lm,state)
        print(self.lm_status_dic)
    

  def GenNewTab(self,widget_lst):
      new_widget = qt.QWidget()
      vb = qt.QVBoxLayout(new_widget)
      hb = qt.QHBoxLayout(new_widget)

      scr_box = qt.QScrollArea()
      vb.addWidget(scr_box)
      vb.addLayout(hb)

      sa = qt.QPushButton('Select all tab')
      sa.connect('clicked(bool)', self.SelectAllTab)
      hb.addWidget(sa)

      ca = qt.QPushButton('Clear all tab')
      ca.connect('clicked(bool)', self.ClearAllTab)
      hb.addWidget(ca)


      wid = qt.QWidget()
      vb2 = qt.QVBoxLayout()
      for widget in widget_lst:
        vb2.addWidget(widget)
      wid.setLayout(vb2)

      scr_box.setVerticalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOn)
      scr_box.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
      scr_box.setWidgetResizable(True)
      scr_box.setWidget(wid)

      return new_widget

  def SelectAllTab(self):
    for cb,lm in self.check_box_dic.items():
        state = True
        self.UpdateLmSelect(lm,state)

  def ClearAllTab(self):
    for cb,lm in self.check_box_dic.items():
        state = False
        self.UpdateLmSelect(lm,state)


  def UpdateLmSelect(self,lm_id,state):
    for cb in self.lm_cb_dic[lm_id]:
      cb.setChecked(state)
    self.lm_status_dic[lm_id] = state
    # print(self.lm_status_dic)

  def UpdateAll(self,state):
    for lm_id,cb_lst in self.lm_cb_dic.items():
      for cb in cb_lst:
        cb.setChecked(state)
      self.lm_status_dic[lm_id] = state

  def SelectAll(self):
    self.UpdateAll(True)
  
  def ClearAll(self):
    self.UpdateAll(False)

  def Get_selected_tooth(self):
    lst_selected_tooth = []
    for tooth_state in self.lm_status_dic.items():
      if tooth_state[1] == True :
        lst_selected_tooth.append(tooth_state[0])
    # print(lst_selected_tooth)
    return lst_selected_tooth

class TableView:
  def __init__(self):
    self.tab_wi = qt.QTableWidget()
    

  def create_tab(self):
    self.tab_wi.setRowCount(10)
    self.tab_wi.setColumnCount(10)
    


 
    
def GetAvailableLm(mfold,lm_group):
  brain_dic = GetBrain(mfold)
  # print(brain_dic)
  available_lm = {"Other":[]}
  for lm in brain_dic.keys():
    if lm in lm_group.keys():
      group = lm_group[lm]
    else:
      group = "Other"
    if group not in available_lm.keys():
      available_lm[group] = [lm]
    else:
      available_lm[group].append(lm)

  return available_lm,brain_dic

def GetLandmarkGroup(group_landmark):
  lm_group = {}
  for group,labels in group_landmark.items():
    for label in labels:
        lm_group[label] = group
  return lm_group

def GetBrain(dir_path):
  brainDic = {}
  normpath = os.path.normpath("/".join([dir_path, '**', '']))
  for img_fn in sorted(glob.iglob(normpath, recursive=True)):
      #  print(img_fn)
      if os.path.isfile(img_fn) and ".pth" in img_fn:
          lab = os.path.basename(os.path.dirname(os.path.dirname(img_fn)))
          num = os.path.basename(os.path.dirname(img_fn))
          if lab in brainDic.keys():
              brainDic[lab][num] = img_fn
          else:
              network = {num : img_fn}
              brainDic[lab] = network

  # print(brainDic)
  out_dic = {}
  for l_key in brainDic.keys():
      networks = []
      for n_key in range(len(brainDic[l_key].keys())):
          networks.append(brainDic[l_key][str(n_key)])

      out_dic[l_key] = networks

  return out_dic




#
# AQ3DCLogic
#

class AQ3DCLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Above' if invert else 'Below'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    slicer.mrmlScene.RemoveNode(cliNode)

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# AQ3DCTest
#

class AQ3DCTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_AQ3DC1()

  def test_AQ3DC1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('AQ3DC1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = AQ3DCLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
