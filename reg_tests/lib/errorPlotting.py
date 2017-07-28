#
# Copyright 2017 National Renewable Energy Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
    This program plots the output vectors (vs. time) of a given solution attribute
    for two OpenFAST solutions, with the second solution assumed to be the baseline for
    comparison. It reads two OpenFAST binary output files (.outb), and
    generates three plots of the given attribute (1) comparing the two tests' respective
    values, (2) showing the difference in values, and (3) showing relative difference,
    as compared to the baseline solution.

    Usage: python plotOpenfastOut.py solution1 solution2 attribute
    Example: python plotOpenfastOut.py output-local/Test01.outb output-baseline/Test01.outb Wind1VelX
"""

import sys
import os
import numpy as np
from fast_io import load_output
import matplotlib.pyplot as plt
import rtestlib as rtl

def validateAndExpandInputs(argv):
    rtl.validateInputOrExit(argv, 3, "solution1 solution2 attribute")
    testSolution = argv[0]
    baselineSolution = argv[1]
    attribute = argv[2]
    rtl.validateFileOrExit(testSolution)
    rtl.validateFileOrExit(baselineSolution)
    return (testSolution, baselineSolution, attribute)
    
def parseSolution(solution):
    try:
        data, info = load_output(solution)
        return (data, info)
    except Exception as e:
        rtl.exitWithError("Error: {}".format(e))
    
def plotError(xseries, y1series, y2series, title, xlabel, y1label, y2label):
    diff = y1series - y2series
    plt.figure()
    plt.subplot(211)
    plt.title(title)
    plt.grid(True)
    plt.ylabel(y1label)
    plt.plot(xseries, y1series, "g", linestyle="solid", linewidth=3, label = "Baseline")
    plt.plot(xseries, y2series, "r", linestyle="solid", linewidth=1, label = "Local")
    plt.legend()
    plt.subplot(212)
    plt.grid(True)
    plt.plot(xseries, diff)
    plt.ylabel(y2label)
    plt.xlabel(xlabel)
    return plt

def savePlot(plt, path, foutname):
    plt.savefig(os.path.join(path, foutname+".png"))
    
def plotOpenfastError(testSolution, baselineSolution, attribute):
    testSolution, baselineSolution, attribute = validateAndExpandInputs([testSolution, baselineSolution, attribute])
    dict1, info1 = parseSolution(testSolution)
    dict2, info2 = parseSolution(baselineSolution)
    
    try:
        channel = info1['attribute_names'].index(attribute)
    except Exception as e:
        rtl.exitWithError("Error: Invalid channel name--{}".format(e))
        
    # get test name -- this could break if .outb file is not used
    testname = testSolution.split("/")[-1]
    testname = testname.split(".")[-2]
    xlabel = 'Time (s)'
    y1label = attribute + " (" + info1["attribute_units"][channel] + ")"
    y2label = "Baseline - Local (" + info1['attribute_units'][channel] + ")"
    
    timevec = dict1[:, 0]
    y1series = np.array(dict1[:, channel], dtype = np.float)
    y2series = np.array(dict2[:, channel], dtype = np.float)
    plt = plotError(timevec, y1series, y2series, testname, xlabel, y1label, y2label)
    
    basePath = os.path.sep.join(testSolution.split(os.path.sep)[:-1])
    plotPath = os.path.join(basePath, "plots")
    rtl.validateDirOrMkdir(plotPath)
    savePlot(plt, plotPath, attribute)
    
def initializePlotDirectory(testSolution, plotList):
    basePath = os.path.sep.join(testSolution.split(os.path.sep)[:-1])
    plotPath = os.path.join(basePath, "plots")
    rtl.validateDirOrMkdir(plotPath)
    with open(os.path.join(plotPath, "Plots.md"), "w") as plotsmd:
        plotsmd.write("These plots were generated automatically.  ")
        plotsmd.write("The plots included are:  ")
        for plot in plotList:
            plotsmd.write(plot + "  \n")
        for plot in plotList:
            plotsmd.write("![alt text][{}]  ".format(plot) + "  \n")
        for plot in plotList:
            plotsmd.write("[{}]: {}".format(plot, os.path.join(plot+".png")) + "\n")

    plotsmd.close()
        