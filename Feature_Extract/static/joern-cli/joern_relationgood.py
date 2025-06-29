import os
import re
import numpy as np

"""
After joern processes the c code, use this code;
0 represents AST, 1 represents CFG, 2 represents PDG
"""
def graphRelation(rootpath, output_path, tag):
    files = os.listdir(rootpath)
    for file in files:
        nodeRelation = []
        nodeInformation = []
        path = rootpath + r'/' + file
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = str(f.read())
                alllist = lines.split("),List(")
                # Determine whether the data is empty
                node1 = []
                node2 = []
                relation = []
                if alllist[1] == "":
                    continue
                else:
                    # extract base file name + function name
                    filename = alllist[0].split("/")[-1]
                    num = filename.index('.c', filename.find('.c') + 1)
                    filename = filename[:num]

                    # add edge for AST, CFG, PDG
                    nodeRelation.append(alllist[1])
                    nodeRelation.append(alllist[3])
                    nodeRelation.append(alllist[5])
                    
                    # add node: node informations
                    nodeInformation.append(alllist[2])
                    nodeInformation.append(alllist[4])
                    nodeInformation.append(alllist[6])

                    # Regular processing
                    nodeRelation    = re.findall(r"\(\d*,\d*,\d*\)", str(nodeRelation))
                    nodeInformation = re.findall(r"\(\d*,.*?\)",     str(nodeInformation))

                    # Remove duplicate nodes
                    nodeInformation = list(set(nodeInformation))

                    # Extract the contents of each column into list => batch processing
                    nodeRelation = ' '.join(nodeRelation)
                    b = re.findall(r'\d+', nodeRelation)
                    for i in range(0, len(b), 3):
                        node1.append(b[i])
                        node2.append(b[i + 1])
                        relation.append(b[i + 2])
                    # relation_matrix = np.vstack([node1, node2, relation]).T

                    nodes = []
                    means = []
                    for i in nodeInformation:
                        node = re.search(r'\d+(?=,)', i)
                        mean = re.search(r'(?<=,).*', i)
                        nodes.append(node.group())
                        means.append(mean.group())
                    # feature_matrix = np.vstack([nodes,means]).T

                    # Replace node numbers -> Re-indexing Nodes to 0...N-1
                    new_node1 = []
                    new_node2 = []
                    new_nodes = list(range(0, len(nodes)))
                    for x in node1:
                        for i in range(len(nodes)):
                            if x == nodes[i]:
                                # new_node1.append(x.replace(str(x), str(i)))
                                new_node1.append(str(i))
                                break
                    for x in node2:
                        for i in range(len(nodes)):
                            if x == nodes[i]:
                                # new_node2.append(x.replace(str(x), str(i)))
                                new_node2.append(str(i))
                                break

                    # write to file
                    if os.path.exists(output_path) == False:
                        os.makedirs(output_path)
                    with open(output_path +"/"+ filename + ".txt", 'w', encoding='utf-8') as f1:
                        for x, y, z in zip(new_node1, new_node2, relation):
                            # for x, y, z in zip(node1, node2, relation):
                            f1.write('(' + x + ',' + y + ',' + z + ')')
                            # f1.write(x + ',' + y + ',' + z)
                            f1.write("\n")
                        f1.write("-----------------------------------")
                        f1.write("\n")
                        for x, y in zip(new_nodes, means):
                            # for x, y in zip(nodes, means):
                            f1.write('(' + str(x) + ',' + y)
                            # f1.write(str(x) + ',' + y)
                            f1.write(("\n"))
                        f1.write('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                        f1.write("\n")
                        if tag == 'good':
                            f1.write('0')
                        elif tag == 'bad':
                            f1.write('1')
        except Exception as e :
            print(e)

if __name__ == '__main__':
    dataPath = r"raw_result/good"
    outPath  = r"result/good"
    # bad or good
    dataTag = 'good'
    graphRelation(dataPath, outPath, dataTag)
    print("joern_relationgood.py over...")





