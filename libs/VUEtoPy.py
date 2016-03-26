from sys import argv, exit
import xml.etree.ElementTree as ET
from libs.IO import rgb
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

def VUEtoPyConverter(input_vue, (prehook, posthook)):
    xml = ""
    started = False
    #Clean garbage
    for line in open(input_vue, 'r'):
        if "<?xml" in line:
            started = True
        if started:
            xml += line

    variables_load = ""
    node_neuron_map = {}
    neurons = []
    synapses = []
    stims_link = {}
    stims = {}
    to_save = []
    sensory_neurons = {}
    sens_map_in = {}; sens_rev_map_in = {};
    sens_map_out = {}; sens_rev_map_out = {};
    tree = ET.fromstring(xml)
    self_connection = []
    for child in tree.findall("child"):
        is_stim = False; is_sensory = False; is_none = False; is_neuron = False; self_connect = False
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
                            elif child.findall("shape")[0].attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "rhombus":
                                variables_load = child.attrib["label"]
                                is_none = True
                            elif child.findall("shape")[0].attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "flag2": #Self
                                is_neuron = True
                                self_connect = True                                
                            else:
                                is_neuron = True
                if is_sensory:
                    sensory_neurons[child.attrib["ID"]] = child.attrib["label"]
                elif is_neuron:
                    if self_connect:
                        self_connection.append(child.attrib["ID"])
                    else:
                        node_neuron_map[child.attrib["ID"]] = len(neurons)
                        new = neuron(child.attrib["ID"])
                        new.neuron_type(child.attrib["label"])
                        neurons.append(new)
                        for prop in child.findall("fillColor"):
                            color = rgb(prop.text.replace("#",""))
                            max_component = max(color)
                            if max_component:
                                to_save.append(child.attrib["ID"])
                        #Unused
#                            if colors.MAP[color.index(max_component)] == "R":
#                                conn_type = "excitatory"
#                            elif colors.MAP[color.index(max_component)] == "B":
#                                conn_type = "inhibitory"
#                            else:
#                                conn_type = "undefined"

                else: #Stim
                    if not child.attrib["ID"] in stims:
                        stims[child.attrib["ID"]] = []
                    try:
                        stims[child.attrib["ID"]].append(child.attrib["label"].split(":")[1].split(","))
                    except IndexError:
                        stims[child.attrib["ID"]].append(child.attrib["label"].split(","))
            #Link
            elif child.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == "link":
                for x_from in child.findall("ID1"):
                    link_from = x_from.text
                for x_to in child.findall("ID2"):
                    link_to = x_to.text
                if link_to in self_connection:
                     link_to = link_from
                try:
                    s_type = child.attrib["label"]
                    if not s_type == "Spike":
                       syn = True; sens = False
                    else:
                        syn = False; sens = True
                except KeyError:
                    syn = False; sens = False
                if syn and link_to:
                    new = synapse((link_from, link_to))
                    new.synapse_type(s_type)
                    synapses.append(new)
                elif sens:
                    if link_from in sensory_neurons: #has output, is an input
                        sens_map_in[link_to] = link_from
                        if not link_from in sens_rev_map_in:
                            sens_rev_map_in[link_from] = []
                        sens_rev_map_in[link_from].append(link_to)
                    elif link_to in sensory_neurons: #has input, is an output
                        sens_map_out[link_from] = link_to
                        if not link_to in sens_rev_map_out:
                            sens_rev_map_out[link_to] = []
                        sens_rev_map_out[link_to].append(link_from)

                else:
                    if not link_from in stims_link:
                        stims_link[link_from] = []
                    stims_link[link_from].append(link_to)

    #Init
    #TODO: Add a posthook? and move the pre before anything
    net_content = "\nfrom libs.templates import * #For ease of use, this line is mandatory\n\
from libs.FasterPresets import _S, _stimuli, _typicalN\n"

    #PreHook
    net_content += "\n#PreHooks:\n" + prehook + "\n"

    #Load variables (contained in the rhombus) before anything else.
    #This way they can be replaced by the prehook
    net_content += "#Variables Loaded from the rhombus\n%s\n" % variables_load 

    #PreHook
    net_content += "\n#PostHooks:\n" + posthook + "\n"

    #Name
    for filename in input_vue.split("."):
        if filename:
            net_name = filename
            break


    net_content += "\nname = \"%s\"\n" % net_name

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
    net_content += "sensory_neurons = [ #0 = ins, #1 = outs\n"

    net_content += "[ #ins (std, Joint, min_angle, max_angle, [dests])\n"
    for key, val in sensory_neurons.iteritems():
        if key in sens_rev_map_in:
            outs = ", ".join([str(node_neuron_map[i]) for i in sens_rev_map_in[key]])
            values = val.split(", ")
            net_content += "\t[ " + ", ".join(values[0:2]) + " ," + values[2] + ", " + values[3] + ", [" + outs + "], ],\n"

    net_content += "],\n"
    net_content += "[ #outs (joint, [inputs])\n"

    for key, val in sensory_neurons.iteritems(): #FIXME: output neurons
        if key in sens_rev_map_out:
            ins = ", ".join([str(node_neuron_map[i]) for i in sens_rev_map_out[key]])
            net_content += "\t[ " + sensory_neurons[key] + ", [" + ins + "] ],\n"

    net_content += "]\n"

    net_content += "]\n\n"
    #Save all

    #net_content += "save = range(0, len(neurons[0]))\n"
    #Don't save whited nodes
    net_content += "save = [ " + ", ".join([ str(node_neuron_map[ts]) for ts in to_save]) + " ]\n\n"

    #Synapses
    net_content += "synapses = [\n"
    tot = len(synapses)
    t = 0
    for s in synapses:
        t += 1
        added = False
        try:
            if s.x_to in self_connection:
                s.x_to = s.x_from
            try: #FIXME: how to use variables in synapses?
                #Synapse tuple or variable-name, copy as-is (removing the marker $)
                if "," in s.s_type or "$" in s.s_type:
                    syn_type = s.s_type.translate(None, '$')
                else: #just a string, convert to synapse
                    syn_type = "_S(\"%s\")" % s.s_type
            except:
                raise

            net_content +=  "    [ %s, [%s], %s" % (node_neuron_map[s.x_from],
                                                node_neuron_map[s.x_to],
                                                     syn_type)
            net_content += "]"
            added = True

        except KeyError:
            print("ERROR: Remembrer not to use labels on Stimulation arrows\nFix the config")
            print("Not adding synapse %s -> %s" % (s.x_from, s.x_to))
            pass

        if t != tot and added:
            net_content += ",\n"
        elif added:
            net_content += "\n"
    net_content += "]\n"

    #No input right now
    net_content += "\nstep_input = _stimuli([\n"
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
                if len(i) == 3:
                    stim_values = "(\t%s,\t%s,\t%s)" % (i[0], i[1], i[2])
                else: #It's a variable. Copy as-is
                    stim_values = "\t%s" % (i[0])
                net_content += "\t[%s,\t%s\t]" % (stim_neuron[0], stim_values)
                net_content += ",\n"

    net_content += "\n])\n"
    net_content += "step_spike = {}\n" #TODO: implement

    out_content = open(output_folder + "/" + net_name + ".py", 'w+')
    out_content.write(net_content)
    print "File created: %s/%s.py" % (output_folder, net_name )
