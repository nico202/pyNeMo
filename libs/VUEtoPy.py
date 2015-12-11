from sys import argv, exit
import xml.etree.ElementTree as ET
import libs.colors as colors
output_folder = "."
class neuron():
    def __init__(self, number):
        self.number = number
    def neuron_type(self, nt):
        self.n_type = nt

class synapse():
    def __init__(self, (x_from, x_to)):
        self.x_from, self.x_to = (x_from, x_to)
    def synapse_type(self, st):
        self.s_type = st

def VUEtoPyConverter(input_vue):
    xml = ""
    started = False
    for line in open(input_vue, 'r'):
        if "<?xml" in line:
            started = True
        if started:
            xml += line

    node_neuron_map = {}
    neurons = []
    synapses = []
    stims_link = {}
    stims = {}
    to_save = []
    sensory_neurons = {}
    sens_map = {}; sens_rev_map = {}
    tree = ET.fromstring(xml)
    for child in tree.findall("child"):
        is_stim = False; is_sensory = False
        if "{http://www.w3.org/2001/XMLSchema-instance}type" in child.attrib:
            if child.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "node":
                if child.findall("shape"):
                    if child.findall("shape")[0] == "":
                        print "No"
                    else:
                        if "{http://www.w3.org/2001/XMLSchema-instance}type" in child.findall("shape")[0].attrib:
                            if child.findall("shape")[0].attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "rectangle":
                                is_stim = True
                            elif child.findall("shape")[0].attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "chevron":
                                is_sensory = True
                if is_sensory:
                    sensory_neurons[child.attrib["ID"]] = child.attrib["label"]
                elif not is_stim or (not is_stim and not "Stim" in child.attrib["label"]):
                    node_neuron_map[child.attrib["ID"]] = len(neurons)
                    new = neuron(child.attrib["ID"])
                    new.neuron_type(child.attrib["label"])
                    neurons.append(new)
                    for prop in child.findall("fillColor"):
                        color = colors.rgb(prop.text.replace("#",""))
                        max_component = max(color)
                        if max_component:
                            to_save.append(child.attrib["ID"])
                        if colors.MAP[color.index(max_component)] == "R":
                            conn_type = "excitatory"
                        elif colors.MAP[color.index(max_component)] == "B":
                            conn_type = "inhibitory"
                        else:
                            conn_type = "undefined"
                        #print "Connection is: %s" % conn_type
                else: #Stim
                    if not child.attrib["ID"] in stims:
                        stims[child.attrib["ID"]] = []
                    try:
                        stims[child.attrib["ID"]].append(child.attrib["label"].split(":")[1].split(","))
                    except IndexError:
                        stims[child.attrib["ID"]].append(child.attrib["label"].split(","))

            elif child.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "link":
                for x_from in child.findall("ID1"):
                    link_from = x_from.text
                for x_to in child.findall("ID2"):
                    link_to = x_to.text
                syn = False; sens = False
                try:
                    s_type = child.attrib["label"]
                    if not s_type == "Spike":
                        syn = True; sens = False
                    else:
                        syn = False; sens = True
                except KeyError:
                    syn = False; sens = False
                if syn:
                    new = synapse((link_from, link_to))
                    new.synapse_type(s_type)
                    synapses.append(new)
                elif sens:
                    sens_map[link_to] = link_from
                    if not link_from in sens_rev_map:
                        sens_rev_map[link_from] = []
                    sens_rev_map[link_from].append(link_to)
                else:
                    if not link_from in stims_link:
                        stims_link[link_from] = []
                    stims_link[link_from].append(link_to)

    net_content = ""
    #Init
    net_content += "from templates import * #For ease of use, this line is mandatory\n\
from libs.FasterPresets import _S, _stimuli\n"

    #Name
    net_name = input_vue.split(".")[0]
    net_content += "name = \"%s\"\n" % net_name
    #Neurons
    net_content += "neurons = [\n"
    tot = len(neurons)
    t = 0
    for n in neurons:
        t += 1
        net_content += "    " + n.n_type + "\n"
        if t != tot:
            net_content += " +\n"
    net_content += "]\n"

    #sensory_neurons
    net_content += "sensory_neurons = [\n"
    for key, val in sensory_neurons.iteritems():
        try:
            for s in sens_rev_map[key]:
                values = val.split(", ")

                syn_type = "_S( \"" + values[3] + "\" )"
                net_content += "\t[ " + ", ".join(values[0:3]) + ", " +str(node_neuron_map[s]) + ", " + syn_type + " ],\n"
        except KeyError:
            print key
    net_content += "]\n\n"

    #Save all

    #net_content += "save = range(0, len(neurons[0]))\n"
    #Don't save whited nodes
    net_content += "save = [ " + ", ".join([ str(node_neuron_map[ts]) for ts in to_save]) + " ]\n\n"
    #No input right now
    net_content += "step_input = _stimuli([\n"
    tot = len(stims_link)
    t = 0
    for s in stims_link:
        t += 1
        for d in stims_link[s]:
            stim_neuron = node_neuron_map[d],
            t2 = len(stims[s])
            l = 0
            for i in stims[s]:
                l += 1
                net_content += "\t[%s,\t%s,\t%s,\t%s]" % (stim_neuron[0], i[0], i[1], i[2])
                net_content += ",\n"

    net_content += "\n])\n"
    net_content += "step_spike = {}\n" #TODO: implement

    #Synapses
    net_content += "synapses = [\n"
    tot = len(synapses)
    t = 0
    for s in synapses:
        t += 1
        try:
            net_content +=  "    [ %s, [%s], _S(\"%s\")" % (node_neuron_map[s.x_from],
                                                node_neuron_map[s.x_to],
                                                s.s_type)
        except KeyError:
            exit("ERROR: Remembrer not to use labels on Stimulation arrows\nFix the config")

        net_content += "]"
        if t != tot:
            net_content += ",\n"
        else:
            net_content += "\n"
    net_content += "]\n"

    out_content = open(output_folder + "/" + net_name + ".py", 'w+')
    out_content.write(net_content)
    print "File created: %s%s.py" % (output_folder, net_name )