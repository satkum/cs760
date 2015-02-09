from __future__ import division
from operator import itemgetter
import arff, math, copy


NEG_INF = -500000 # Replace with a proper negative infinity later

def getAttrIndex(attributes, attributeName):
    index = 0
    for attr in attributes:
        if attr[0] == attributeName:
            break
        else:
            index = index+1

    return index

# def splitContinuousAttributes(dataRows, attrIndex):
#     s = sorted(dataRows, key=itemgetter(attrIndex))
#     groupStart = 0
#     current = s[0][-1]
#     splitA = {}
#     for i in range(0,len(s)-2):
#         if s[i][-1] == current:
#             continue
#         else:
#             threshold = (s[i-1][attrIndex] + s[i][attrIndex])/2
#             if threshold in splitA:
#                 splitA[threshold].append(s[groupStart:i])
#             else:
#                 splitA[threshold] = s[groupStart:i]
#             groupStart = i
#             current = s[i][-1]

#     return splitA

def splitContinuousAttributes(dataRows, attrIndex):
    s = sorted(dataRows, key=itemgetter(attrIndex))
    current = s[0][-1]
    splitA = {}
    for i in range(0,len(s)-2):
        if s[i][-1] == current:
            continue
        else:
            threshold = (s[i-1][attrIndex] + s[i][attrIndex])/2
            splitA[threshold] = []
            splitA[threshold].append(s[0:i])
            splitA[threshold].append(s[i:len(dataRows)])
            current = s[i][-1]

    return splitA

def entropy(dataRows, classValues):
    classData = {}
    for val in classValues:
        classData[val] = []

    for row in dataRows:
        classData[row[-1]].append(row)

    entropy = 0

    totalRows = len(dataRows)
    if totalRows == 0:
        return 0

    for val in classValues:
        fraction = len(classData[val])/totalRows
        try:
            entropy = entropy - (fraction * math.log(fraction,2))
        except ValueError:
            return 0

    return entropy

def infoGain(dataRows, classValues, attributes, attributeName, attrValues):
    attrData = {}
    attrIndex = getAttrIndex(attributes, attributeName)

    entropyS = entropy(dataRows, classValues)
    gain = entropyS
    threshold = None
    totalRows = len(dataRows)
    if isinstance(attrValues, list):
        for val in attrValues:
            attrData[val] = []
        
        for row in dataRows:
            attrData[row[attrIndex]].append(row)

        for val in attrValues:
            valEntropy = entropy(attrData[val], classValues)
            fraction = len(attrData[val])/totalRows
            gain = gain - (fraction * valEntropy)
        
        continuous = False
        print "nominal \n"
    else:
        assert attrValues == 'REAL'
        continuous = True
        print "continuous \n"
        splits = splitContinuousAttributes(dataRows, attrIndex)
        maxGain = NEG_INF
        for split,values in splits.items():
            localGain = entropyS
            for val in values:
                valEntropy = entropy(val, classValues)
                fraction = len(val)/totalRows
                localGain = localGain - (fraction * valEntropy)

            if localGain > maxGain:
                maxGain = localGain
                threshold = split


        gain = maxGain

    return [gain, threshold, continuous]

###  Main script ###

rawData = arff.load(open('heart_train.arff', 'rb'))

classValues = rawData['attributes'][-1][1]

entropyS = entropy(rawData['data'], classValues)

numAttrs = len(rawData['attributes'])-1 
attrs = rawData['attributes'][:numAttrs]
print attrs
print "\n== E S == \n"
print entropyS
print "\n======\n"

selectedAttr = {'gain' : NEG_INF, 'threshold' : None, 'continuous' : None, 'name' : None, 'values': None}
for attr in attrs:
    g = infoGain(rawData['data'], classValues, attrs, attr[0], attr[1])
    print g
    if g[0] > selectedAttr['gain']:
        selectedAttr['gain'] = g[0]
        selectedAttr['threshold'] = g[1]
        selectedAttr['continuous'] = g[2]
        selectedAttr['name'] = attr[0]
        selectedAttr['values'] = attr[1]
    print attr[0]


print 'selectedAttr'
print selectedAttr

