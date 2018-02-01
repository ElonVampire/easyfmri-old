#!/usr/bin/env python3
import os
import sys
import time
import numpy as np
import scipy.io as io
from PyQt5.QtWidgets import *
from sklearn import preprocessing
from Base.dialogs import LoadFile, SaveFile
from Base.utility import getVersion, getBuild, strRange, SimilarityMatrixBetweenClass
from RSA.DeepGroupRSA import DeepGroupRSA
from GUI.frmMADeepGroupRSAGUI import *

# Plot
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


class frmMADeepGroupRSA(Ui_frmMADeepGroupRSA):
    ui = Ui_frmMADeepGroupRSA()
    dialog = None
    # This function is run when the main form start
    # and initiate the default parameters.
    def show(self):
        global dialog
        global ui
        ui = Ui_frmMADeepGroupRSA()
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        dialog = QtWidgets.QMainWindow()
        ui.setupUi(dialog)
        self.set_events(self)
        ui.tabWidget.setCurrentIndex(0)

        # Activation
        ui.cbActivation.addItem('ReLU', 'relu')
        ui.cbActivation.addItem('Sigmoid', 'sigmoid')
        ui.cbActivation.addItem('Tanh', 'tanh')

        # LASSO Norm
        ui.cbLossNorm.addItem('Euclidean', 'euclidean')
        ui.cbLossNorm.addItem('Supremum', np.inf)

        # Device
        ui.cbDevice.addItem("Auto", False)
        ui.cbDevice.addItem("Just CPU", True)


        dialog.setWindowTitle("easy fMRI Group Level Single-Deep-Kernel Representational Similarity Analysis - V" + getVersion() + "B" + getBuild())
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        dialog.setFixedSize(dialog.size())
        dialog.show()


    # This function initiate the events procedures
    def set_events(self):
        global ui
        ui.btnClose.clicked.connect(self.btnClose_click)
        ui.btnInFile.clicked.connect(self.btnInFile_click)
        ui.btnOutFile.clicked.connect(self.btnOutFile_click)
        ui.btnConvert.clicked.connect(self.btnConvert_click)
        ui.btnRedraw.clicked.connect(self.btnRedraw_click)


    def btnClose_click(self):
        global dialog
        dialog.close()


    def btnInFile_click(self):
        filename = LoadFile("Load MatLab data file ...",['MatLab files (*.mat)'],'mat',\
                            os.path.dirname(ui.txtInFile.text()))
        if len(filename):
            if os.path.isfile(filename):
                try:
                    print("Loading ...")
                    data = io.loadmat(filename)
                    Keys = data.keys()

                    # Data
                    ui.txtData.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtData.addItem(key)
                        if key == "data":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtData.setCurrentText("data")
                        print("Data Shape: ", np.shape(data["data"]))


                    # Label
                    ui.txtLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtLabel.addItem(key)
                        if key == "label":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtLabel.setCurrentText("label")
                        Labels = data[ui.txtLabel.currentText()]
                        Labels = np.unique(Labels)
                        print("Number of labels: ", np.shape(Labels)[0])
                        print("Labels: " ,Labels)
                        ui.txtClass.clear()
                        for lbl in Labels:
                            ui.txtClass.append(str(lbl))

                    # Design
                    ui.txtDesign.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtDesign.addItem(key)
                        if key == "design":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtDesign.setCurrentText("design")

                    # Subject
                    ui.txtSubject.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtSubject.addItem(key)
                        if key == "subject":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtSubject.setCurrentText("subject")
                        print("Number of subjects: ", np.shape(np.unique(data["subject"]))[0])

                    # Run
                    ui.txtRun.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtRun.addItem(key)
                        if key == "run":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtRun.setCurrentText("run")

                    # Counter
                    ui.txtCounter.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtCounter.addItem(key)
                        if key == "counter":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtCounter.setCurrentText("counter")

                    # Task
                    ui.txtTask.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtTask.addItem(key)
                        if key == "task":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtTask.setCurrentText("task")

                    ui.txtInFile.setText(filename)
                    print("DONE.")
                except Exception as e:
                    print(e)
                    print("Cannot load data file!")
                    return
            else:
                print("File not found!")

    def btnOutFile_click(self):
        ofile = SaveFile("Save result file ...",['Result files (*.mat)'],'mat',\
                             os.path.dirname(ui.txtOutFile.text()))
        if len(ofile):
            ui.txtOutFile.setText(ofile)


    def btnConvert_click(self):
        msgBox = QMessageBox()
        tStart = time.time()
        Activation  = ui.cbActivation.currentData()
        LossNorm    = ui.cbLossNorm.currentData()
        try:
            Layers = strRange(ui.txtLayers.text(),Unique=False)
            if Layers is None:
                raise Exception('')

        except:
            msgBox.setText("Layers is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            KIter = np.int32(ui.txtKIter.text())
        except:
            msgBox.setText("Number of iteration is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            RIter = np.int32(ui.txtRIter.text())
        except:
            msgBox.setText("Number of iteration is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False


        try:
            BatchSize = np.int32(ui.txtBatch.text())
        except:
            msgBox.setText("Number of batch is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            ReportStep = np.int32(ui.txtReportStep.text())
        except:
            msgBox.setText("Number of Report Step is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False


        try:
            LearningRate = np.float32(ui.txtRate.text())
        except:
            msgBox.setText("Number of Report Step is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False


        if not ui.cbCov.isChecked() and not ui.cbCorr.isChecked():
            msgBox.setText("At least, you must select one metric!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        # Filter
        try:
            Filter = ui.txtFilter.text()
            if not len(Filter):
                Filter = None
            else:
                Filter = Filter.replace("\'", " ").replace(",", " ").replace("[", "").replace("]","").split()
                Filter = np.int32(Filter)
        except:
            print("Filter is wrong!")
            return

        # OutFile
        OutFile = ui.txtOutFile.text()
        if not len(OutFile):
            msgBox.setText("Please enter out file!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        OutData = dict()

        # InFile
        InFile = ui.txtInFile.text()
        if not len(InFile):
            msgBox.setText("Please enter input file!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        if not os.path.isfile(InFile):
            msgBox.setText("Input file not found!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        print("Loading ...")
        InData = io.loadmat(InFile)

        # Data
        if not len(ui.txtData.currentText()):
            msgBox.setText("Please enter Input Data variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        # Label
        if not len(ui.txtLabel.currentText()):
                msgBox.setText("Please enter Train Label variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

        # Design
        if not len(ui.txtDesign.currentText()):
            msgBox.setText("Please enter Input Design variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Design = InData[ui.txtDesign.currentText()]
        except:
            msgBox.setText("Design value is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            X = InData[ui.txtData.currentText()]
            L = InData[ui.txtLabel.currentText()][0]
            if ui.cbScale.isChecked() and not ui.rbScale.isChecked():
                X = preprocessing.scale(X)
                print("Whole of data is scaled X~N(0,1).")


        except:
            print("Cannot load data or label")
            return

        # Task
        if not len(ui.txtTask.currentText()):
                msgBox.setText("Please enter Task variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
        try:
            TaskTitle = InData[ui.txtTask.currentText()][0]
        except:
            msgBox.setText("Task variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        TaskTitleUnique = np.unique(TaskTitle)
        Task = np.zeros(np.shape(TaskTitle))

        for ttinx, tt in enumerate(TaskTitle):
            for ttlinx, ttl in enumerate(TaskTitleUnique):
                if tt[0] == ttl:
                    Task[ttinx] = ttlinx + 1
                    break

        # Subject
        if not len(ui.txtSubject.currentText()):
            msgBox.setText("Please enter Subject variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Sub = InData[ui.txtSubject.currentText()][0]
        except:
            msgBox.setText("Subject variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        # Run
        if not len(ui.txtRun.currentText()):
            msgBox.setText("Please enter Run variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Run = InData[ui.txtRun.currentText()][0]
        except:
            msgBox.setText("Run variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        # Counter
        if not len(ui.txtCounter.currentText()):
            msgBox.setText("Please enter Counter variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            Con = InData[ui.txtCounter.currentText()][0]
        except:
            msgBox.setText("Counter variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False


        if Filter is not None:
            for fil in Filter:
                # Remove Training Set
                labelIndx = np.where(L == fil)[0]
                Design = np.delete(Design, labelIndx, axis=0)
                X = np.delete(X, labelIndx, axis=0)
                L = np.delete(L, labelIndx, axis=0)
                Task = np.delete(Task, labelIndx, axis=0)
                Sub = np.delete(Sub, labelIndx, axis=0)
                Run = np.delete(Run, labelIndx, axis=0)
                Con = np.delete(Con, labelIndx, axis=0)
                print("Class ID = " + str(fil) + " is removed from data.")

        try:
            Unit = np.int32(ui.txtUnit.text())
        except:
            msgBox.setText("Unit for the test set must be a number!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        if Unit < 1:
            msgBox.setText("Unit for the test set must be greater than zero!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        print("Calculating Levels ...")
        GroupFold = None
        FoldStr = ""
        if ui.cbFSubject.isChecked():
            if not ui.rbFRun.isChecked():
                GroupFold = [Sub]
                FoldStr = "Subject"
            else:
                GroupFold = np.concatenate(([Sub],[Run]))
                FoldStr = "Subject+Run"

        if ui.cbFTask.isChecked():
            GroupFold = np.concatenate((GroupFold,[Task])) if GroupFold is not None else [Task]
            FoldStr = FoldStr + "+Task"

        if ui.cbFCounter.isChecked():
            GroupFold = np.concatenate((GroupFold,[Con])) if GroupFold is not None else [Con]
            FoldStr = FoldStr + "+Counter"

        if FoldStr == "":
            FoldStr = "Whole-Data"
            GUFold = [1]
            ListFold = [1]
            UniqFold = [1]
            GroupFold = [1]
            UnitFold = np.ones((1, np.shape(X)[0]))
        else:
            GroupFold = np.transpose(GroupFold)
            UniqFold = np.array(list(set(tuple(i) for i in GroupFold.tolist())))
            FoldIDs = np.arange(len(UniqFold)) + 1

            if len(UniqFold) <= Unit:
                msgBox.setText("Unit must be smaller than all possible levels! Number of all levels is: " + str(len(UniqFold)))
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            if np.mod(len(UniqFold),Unit):
                msgBox.setText("Unit must be divorceable to all possible levels! Number of all levels is: " + str(len(UniqFold)))
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            ListFold = list()
            for gfold in GroupFold:
                for ufoldindx, ufold in enumerate(UniqFold):
                    if (ufold == gfold).all():
                        currentID = FoldIDs[ufoldindx]
                        break
                ListFold.append(currentID)

            ListFold = np.int32(ListFold)
            if Unit == 1:
                UnitFold = np.int32(ListFold)
            else:
                UnitFold = np.int32((ListFold - 0.1) / Unit) + 1

            GUFold = np.unique(UnitFold)


        FoldInfo = dict()
        FoldInfo["Unit"]    = Unit
        FoldInfo["Group"]   = GroupFold
        FoldInfo["Order"]   = FoldStr
        FoldInfo["List"]    = ListFold
        FoldInfo["Unique"]  = UniqFold
        FoldInfo["Folds"]   = UnitFold

        OutData["FoldInfo"] = FoldInfo
        OutData["ModelAnalysis"] = "Tensorflow.Group.Single-Deep-Kernel.RSA"


        print("Number of all levels is: " + str(len(UniqFold)))


        # RSA Method
        OutData['Method'] = dict()
        OutData['Method']['Layers']         = ui.txtLayers.text()
        OutData['Method']['Activation']     = Activation
        OutData['Method']['LossNorm']       = LossNorm
        OutData['Method']['LearningRate']   = LearningRate
        OutData['Method']['KernelIter']     = KIter
        OutData['Method']['RSAIter']        = RIter
        OutData['Method']['BatchSize']      = BatchSize
        OutData['Method']['ReportStep']     = ReportStep
        OutData['Method']['Verbose']        = ui.cbVerbose.isChecked()
        TData = list()
        TReg  = list()
        print("Reshaping Data ...")
        for foldID, fold in enumerate(GUFold):
            print("Reshaping level " + str(foldID + 1)," of ", str(len(UniqFold)) , " ...")
            Index = np.where(UnitFold == fold)
            # Whole-Data
            if FoldStr == "Whole-Data" and np.shape(Index)[0]:
                Index = [Index[1]]
            XLi      = X[Index]
            RegLi    = Design[Index]
            if ui.cbScale.isChecked() and ui.rbScale.isChecked():
                XLi = preprocessing.scale(XLi)
                print("Whole of data is scaled X%d~N(0,1)." % (foldID + 1))

            TData.append(XLi)
            TReg.append(RegLi)

        print("Running Deep Group RSA ...")
        rsa = DeepGroupRSA(layers=Layers, kernel_iter = KIter, rsa_iter = RIter, learning_rate=LearningRate,
                           loss_norm=LossNorm, activation=Activation, \
                          batch_size=BatchSize, report_step=ReportStep, verbose=ui.cbVerbose.isChecked(), \
                           NCat=np.shape(Design)[1], NVoxel=np.shape(X)[1], CPU=ui.cbDevice.currentData())
        Betas, Eps, Weights, Bias, MSE, loss_mat = rsa.fit(data_vals=TData, design_vals=TReg)

        OutData["Weight"]   = Weights
        OutData["Bias"]     = Bias
        OutData["MSE"]      = MSE
        OutData["AMSE"]     = rsa.AMSE
        OutData["MSE_std"]  = np.std(rsa.AMSE)
        OutData["LossMat"]  = loss_mat
        print("Average MSE: %f" % (OutData["MSE"]))

        print("Calculating cov & corr ... ")
        AvgCov  = None
        AvgCorr = None
        for beta_id, beta in enumerate(Betas):
            OutData["BetaL" + str(beta_id)]  = beta
            if ui.cbCov.isChecked():
                co = np.cov(beta)
                OutData["Cov" + str(beta_id)]  = co
                AvgCov = co if AvgCov is None else AvgCov + co

            if ui.cbCorr.isChecked():
                cr = np.corrcoef(beta)
                OutData["Corr" + str(beta_id)] = cr
                AvgCorr = cr if AvgCorr is None else AvgCorr + cr
        for eps_id, ep in enumerate(Eps):
            OutData["EpsL" + str(eps_id)]    = ep

        if ui.cbCov.isChecked():
            AvgCov = AvgCov / len(TData)
            covClass = SimilarityMatrixBetweenClass(AvgCov)
            OutData["Covariance"]       = AvgCov
            OutData["Covariance_min"]   = covClass.min()
            OutData["Covariance_max"]   = covClass.max()
            OutData["Covariance_mean"]  = covClass.mean()
            OutData["Covariance_std"]   = covClass.std()

        if ui.cbCorr.isChecked():
            AvgCorr = AvgCorr / len(TData)
            corClass = SimilarityMatrixBetweenClass(AvgCorr)
            OutData["Correlation"]      = AvgCorr
            OutData["Correlation_min"]  = corClass.min()
            OutData["Correlation_max"]  = corClass.max()
            OutData["Correlation_mean"] = corClass.mean()
            OutData["Correlation_std"]  = corClass.std()


        OutData["RunTime"] = time.time() - tStart
        print("Runtime (s): %f" % (OutData["RunTime"]))
        print("Saving results ...")
        io.savemat(OutFile,mdict=OutData,do_compression=True)
        print("Output is saved.")


        if ui.cbDiagram.isChecked():
            if ui.cbCorr.isChecked():
                fig1 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(AvgCorr, vmin=-0.1, vmax=1)
                plt.xlim([0, np.shape(AvgCorr)[0]])
                plt.ylim([0, np.shape(AvgCorr)[0]])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Deep Group RSA: Correlation\nLevel: ' + FoldStr)
                plt.show()

            if ui.cbCov.isChecked():
                fig2 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(AvgCov)
                plt.xlim([0, np.shape(AvgCov)[0]])
                plt.ylim([0, np.shape(AvgCov)[0]])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Deep Group RSA: Covariance\nLevel: ' + FoldStr)
                plt.show()
        print("DONE.")
        msgBox.setText("Group Level Single-Deep-Kernel Representational Similarity Analysis is done.")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()


    def btnRedraw_click(self):
        msgBox = QMessageBox()

        ofile = LoadFile("Save result file ...",['Result files (*.mat)'],'mat',\
                             os.path.dirname(ui.txtOutFile.text()))
        if len(ofile):
            try:
                Res     = io.loadmat(ofile)
            except:
                print("Cannot load result file!")
                msgBox.setText("Cannot load result file!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            if ui.cbCorr.isChecked():
                try:
                    Corr = Res["Correlation"]
                except:
                    print("Cannot load Correlation variable!")
                    msgBox.setText("Cannot load Correlation variable!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                fig1 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(Corr, vmin=-0.1, vmax=1)
                plt.xlim([0, np.shape(Corr)[0]])
                plt.ylim([0, np.shape(Corr)[0]])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Deep Group RSA: Correlation\nLevel: ' + str(Res["FoldInfo"]["Order"][0][0][0]))
                plt.show()


            if ui.cbCov.isChecked():
                try:
                    Cov = Res["Covariance"]
                except:
                    print("Cannot load Covariance variable!")
                    msgBox.setText("Cannot load Covariance variable!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                fig2 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(Cov)
                plt.xlim([0, np.shape(Cov)[0]])
                plt.ylim([0, np.shape(Cov)[0]])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Deep Group RSA: Covariance\nLevel: ' + str(Res["FoldInfo"]["Order"][0][0][0]))
                plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frmMADeepGroupRSA.show(frmMADeepGroupRSA)
    sys.exit(app.exec_())